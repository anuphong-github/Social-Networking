from django.shortcuts import render,redirect,get_object_or_404
from blog.models import *
from users.models import *
from django.contrib.auth.models import User
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.db.models import Count
from django.contrib.auth.decorators import login_required
import sys

def is_users(post_user,logged_user):
    return post_user == logged_user

PAGINATION_COUNT = 3

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
