from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {'text': forms.Textarea}
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        widgets = {'text': forms.Textarea}
        fields = ('text',)
