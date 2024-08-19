from django import forms
from .models import Thread, Post, Comment

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title']  # Assuming a Thread has a 'title' and no 'content' field

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']  # Ensure 'content' is the correct field name

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # Ensure 'content' is the correct field name
