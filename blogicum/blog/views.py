from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from blogicum.settings import POST_COUNT_LIMIT
from .add_functions import base_query_set
from .models import Post, Category, Comment
from .forms import PostForm, ProfileUpdateForm, CommentForm

UserModel = get_user_model()


class OnlyAuthorOrAdminMixin(UserPassesTestMixin):
    """Только автор и админ"""

    def test_func(self):
        object = self.get_object()
        return (object.author == self.request.user
                or self.request.user.is_superuser)


class OnlyAuthorMixin(UserPassesTestMixin):
    """Только автор"""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user
                

class IndexPostsView(ListView):
    """Главная страница"""
    template_name = 'blog/index.html'
    paginate_by = POST_COUNT_LIMIT
    queryset = base_query_set()


class CategoryPostsView(ListView):
    """Все публикации в категории"""

    model = Post
    paginate_by = POST_COUNT_LIMIT
    template_name = 'blog/category.html'

    def get_queryset(self):
        cur_category = get_object_or_404(
            Category.objects.all().filter(is_published=True,
                                          slug=self.kwargs['category_slug']))
        posts = base_query_set(cur_category.posts.all())
        return posts

    def get_context_data(self, **kwargs):
        cur_category = get_object_or_404(
            Category.objects.all().filter(is_published=True,
                                          slug=self.kwargs['category_slug']))

        context = super().get_context_data(**kwargs)
        context['category'] = cur_category
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание публикации"""

    model = Post
    form_class = PostForm
    template_name = 'posts/create.html'

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'cur_username':
                                    self.request.user.username})


class PostDetailView(DetailView):
    """Детали публикации"""

    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        cur_post = get_object_or_404(base_query_set(in_published_only=False),
                                     id=self.kwargs['post_id'])
        if not cur_post.author == self.request.user:
            cur_post = get_object_or_404(base_query_set(),
                                         id=self.kwargs['post_id'])
        return cur_post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (self.object.comments.select_related('author').
                               order_by('created_at'))
        return context


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование публикации"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect(reverse_lazy('blog:post_detail',
                                     kwargs={'post_id': self.kwargs['post_id']}))

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(OnlyAuthorOrAdminMixin, DeleteView):
    """Удаление публикации"""

    form_class = PostForm
    template_name = 'blog/create.html'
    queryset = base_query_set(in_published_only=False)
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect(reverse_lazy('blog:post_detail',
                                     kwargs={'post_id':
                                             self.kwargs['post_id']}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(self.queryset, id=self.kwargs['post_id'])
        context['form'] = PostForm(instance=post)
        return context

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'cur_username':
                                    self.request.user.username})


class ProfileListView(ListView):
    """Страница пользователя"""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POST_COUNT_LIMIT

    def get_queryset(self):
        cur_user = get_object_or_404(
            UserModel.objects.all().
            filter(username=self.kwargs['cur_username'])
        )
        if self.request.user == cur_user:
            posts = base_query_set(cur_user.posts.all(),
                                   in_published_only=False)
        else:
            posts = base_query_set(cur_user.posts.all())

        return posts

    def get_context_data(self, **kwargs):
        cur_user = get_object_or_404(
            UserModel.objects.all().
            filter(username=self.kwargs['cur_username'])
        )

        context = super().get_context_data(**kwargs)
        context['profile'] = cur_user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля"""

    model = User
    form_class = ProfileUpdateForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'cur_username':
                                    self.request.user.username})  


class BaseCommentView(LoginRequiredMixin):
    """Комментарий"""

    model = Comment
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={'post_id': self.object.post.pk}
        )
    
    def get_object(self, queryset=None):
        return get_object_or_404(Comment.objects.all().
                                 filter(post=self.kwargs['post_id'],
                                        pk=self.kwargs['comment_id']))


class CommentCreateView(BaseCommentView, CreateView):
    """Создание комментария"""

    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        cur_post = get_object_or_404(Post.objects.all().
                                     filter(pk=self.kwargs['post_id']))
        form.instance.post = cur_post
        send_mail(
            subject='Добавлен комментарий к вашей публикации.',
            message=f'Добавлен комментарий к публикации {cur_post.title} !',
            from_email='blog@blogicum.not',
            recipient_list=[cur_post.author.email],
            # recipient_list=['voznaya.olga@yandex.ru'],
            fail_silently=True,
        )
        return super().form_valid(form)


class CommentUpdateView(OnlyAuthorMixin, BaseCommentView, UpdateView):
    """Редактирование комментария"""

    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class CommentDeleteView(OnlyAuthorOrAdminMixin, BaseCommentView, DeleteView):
    """Удаление комментария"""

    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'