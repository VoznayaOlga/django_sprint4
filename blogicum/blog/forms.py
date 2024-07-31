from django import forms
from django.contrib.auth import get_user_model
from django.forms.widgets import DateTimeInput

from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма добавления публикации"""
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': DateTimeInput(attrs={'type': 'datetime-local',
                                             'class': 'form-control'},
                                      format='%Y-%m-%dT%H:%M'),
        }


class ProfileUpdateForm(forms.ModelForm):
    """Форма обновления данных профиля пользователя"""

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'email', 'username')


class CommentForm(forms.ModelForm):
    """Форма добавления комметария"""

    class Meta:
        model = Comment
        fields = ('text',)
