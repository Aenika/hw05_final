from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    labels = {
        'text': 'Текст поста',
        'group': 'Группа'
    }
    help_texts = {
        'text': 'Введите текст поста',
        'group': 'Группа, к которой будет относиться пост'
    }

    class Meta:
        model = Post
        widgets = {'text': forms.Textarea}
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    labels = {
        'text': 'Текст комментария',
    }
    help_texts = {
        'text': 'Введите текст комментария',
    }

    class Meta:
        model = Comment
        widgets = {'text': forms.Textarea}
        fields = ('text',)
