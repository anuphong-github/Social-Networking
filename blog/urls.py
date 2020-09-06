from django.urls import path
from .views import (
    PostView,
    UserPostView,
    PostCreate,
)

urlpatterns = [
    path('',PostView.as_view(),name='blog-index'),
    path('user/<str:username>', UserPostView.as_view(), name='user-posts'),
    path('post/new/',PostCreate.as_view(),name='post-create'),
    
]
