from django.shortcuts import render,redirect,get_object_or_404
from blog.models import *
from users.models import *
from django.contrib.auth.models import User
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.db.models import Count
from django.contrib.auth.decorators import login_required
import sys
from .forms import UserCommentForm

def is_users(post_user,logged_user):
    return post_user == logged_user

PAGINATION_COUNT = 5

class PostView(LoginRequiredMixin,ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = PAGINATION_COUNT

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        all_users = []
        counter = Post.objects.values('author').annotate(author_count=Count('author')).order_by('-author_count')[:6]

        for i in counter:
            all_users.append(User.objects.filter(pk=i['author']).first())
        data['preference'] = Preference.objects.all()
        data['all_users'] = all_users
        return data

    def get_queryset(self):
        user = self.request.user
        qs = Follow.objects.filter(user=user)
        follows = [user]
        for obj in qs :
            follows.append(obj.follow_user)
        return Post.objects.filter(author__in=follows).order_by('-date_posted')

class UserPostView(LoginRequiredMixin,ListView):
    model = Post
    template_name = 'blog/user-posts.html'
    context_object_name = 'posts'
    paginate_by = PAGINATION_COUNT

    def visible_user(self):
        return get_object_or_404(User,username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        visible_user = self.visible_user()
        logged_user = self.request.user

        if logged_user.username == '' or logged_user is None:
            can_follow = False
        else:
            can_follow = (Follow.objects.filter(user=logged_user,follow_user=visible_user).count()==0)

        data = super().get_context_data(**kwargs)
        data['user_profile'] = visible_user
        data['can_follow'] = can_follow
        return data

    def get_queryset(self):
        user = self.visible_user()
        return Post.objects.filter(author=user).order_by('-date_posted')

    def post(self, request, *args, **kwargs):
        if request.user.id is not None:
            follows_between = Follow.objects.filter(user=request.user,follow_user=self.visible_user())

            if 'follow' in request.POST:

                new_relation = Follow(user=request.user, follow_user=self.visible_user())

                if follows_between.count() == 0:
                    new_relation.save()

            elif 'unfollow' in request.POST:

                if follows_between.count() > 0 :
                    follows_between.delete()

        return self.get(self, request, *args, **kwargs)

class PostCreate(LoginRequiredMixin,CreateView):
    model = Post
    fields = ['content']
    template_name = 'blog/post-create.html'
    success_url = '/'
    def form_valid(self,form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag'] = 'Add your post'
        return data

class PostDelete(LoginRequiredMixin, UserPassesTestMixin,DeleteView):
    model = Post
    template_name = 'blog/post-delete.html'
    context_object_name = 'post'
    success_url = '/'

    def test_func(self):
        return is_users(self.get_object().author,self.request.user)

class PostUpdate(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Post
    fields = ['content']
    template_name = 'blog/post-create.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return is_users(self.get_object().author,self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag'] = 'Edit'
        return data

class PostDetail(DetailView):
    model = Post
    template_name = 'blog/post-detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        comments_connected = Comment.objects.filter(post_connected=self.get_object()).order_by('-date_posted')
        data['comments'] = comments_connected
        data['form'] = UserCommentForm(instance=self.request.user)
        return data

    def post(self, request, *args, **kwargs):
        new_comment = Comment(content=request.POST.get('content'),
                              author=self.request.user,
                              post_connected=self.get_object())
        new_comment.save()
        return self.get(self, request, *args, **kwargs)

class Follows(ListView):
    model = Follow
    template_name = 'blog/follow.html'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(User, username = self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['follow'] = 'follows'
        return data

class Followers(ListView):
    model = Follow
    template_name = 'blog/follow.html'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(User, username = self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(follow_user = user).order_by('-date')

    def get_context_data(self, *, objects_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['follow'] = 'followers'
        return data


@login_required
def like(request,post_id,userlike):
        if request.method == "POST":
            each_post = get_object_or_404(Post,id=post_id)
            object_orm = ""
            value_object = ""
            userlike = int(userlike)
            try:
                object_orm = Preference.objects.get(user=request.user,post=each_post)
                value_object = object_orm.value
                value_object = (value_object)
                userlike = int(userlike)
                if value_object != userlike:
                    object_orm.delete()
                    u_pref = Preference()
                    u_pref.user = request.user
                    u_pref.post = each_post
                    u_pref.value = userlike
                    if userlike ==  1 and object_orm != 1:
                        each_post.likes += 1
                        each_post.dislike -= 1
                    u_pref.save()
                    each_post.save()
                    context = {'each_post':each_post,
                                'post_id':post_id}
                    return redirect('blog-index')

                elif value_object == userlike:
                    object_orm.delete()
                    if userlike == 1:
                        each_post.likes -= 1
                    each_post.save()
                    context = {'each_post':each_post,
                                'post_id':post_id}
                    return redirect('blog-index')

            except Preference.DoesNotExist:
                    u_pref = Preference()
                    u_pref.user = request.user
                    u_pref.post = each_post
                    u_pref.value = userlike
                    userlike = int(userlike)
                    if userlike == 1 :
                        each_post.likes += 1
                    u_pref.save()
                    each_post.save()

                    context = {'post':each_post,
                               'post_id':post_id}
                    return redirect('blog-index')
        else:
            each_post = get_object_or_404(Post , id=post_id)
            context = {'each_post':each_hpost,
                        'each_post':post_id}
            return redirect('blog-index')
