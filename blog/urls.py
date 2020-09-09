from django.urls import path
from .views import (
    PostView,
    UserPostView,
    PostCreate,
    PostDelete,
    PostUpdate,
    PostDetail,
    Follows,
    Followers,
)

urlpatterns = [
    path('',PostView.as_view(),name='blog-index'),
    path('user/<str:username>', UserPostView.as_view(), name='user-posts'),
    path('post/new/',PostCreate.as_view(),name='post-create'),
    path('post/<int:pk>/del',PostDelete.as_view(),name='post-delete'),
    path('post/<int:pk>/update/',PostUpdate.as_view(),name='post-update'),
    path('post/<int:pk>/',PostDetail.as_view(),name='post-detail'),
    path('user/<str:username>/follows',Follows.as_view(),name='user-follows'),
    path('user/<str:username>/followers',Followers.as_view(),name='user-followers'),
]
