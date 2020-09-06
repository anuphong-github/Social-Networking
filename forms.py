from django import forms
from .models import Comment

class UserCommentForm(forms.ModelForm):
    class Meta:
        models = Comment
        fields = ['content']
