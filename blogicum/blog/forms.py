from django import forms
# from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.forms.widgets import DateInput


from .models import Post, Comment
# User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма добавления публикации"""

    class Meta:
        model = Post
        exclude = ('author',)
        fields = '__all__'
        widgets = {
            'pub_date': DateInput(attrs={'type': 'date'})
        }


class ProfileUpdateForm(forms.ModelForm):
    """Форма обновления данных профиля пользователя"""

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'email', 'username')
        # exclude = ('password',)
        # fields = '__all__'


class UserUpdateForm(forms.ModelForm):
    """Форма обновления данных пользователя"""

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'email', 'username')
        # fields = '__all__'


class CommentForm(forms.ModelForm):
    """Форма добавления комметария"""

    class Meta:
        model = Comment
        fields = ('text',)
