from django.db.models.base import Model as Model
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.mail import send_mail

from django.core.paginator import Paginator

from .models import Post, Category, Comment
from .constants import POST_COUNT_LIMIT
from .forms import PostForm, ProfileUpdateForm, UserUpdateForm, CommentForm


def base_query_set(model_manager=Post.objects):
    """Базовый запрос"""
    queryset = (model_manager.all().
                select_related('category', 'location', 'author').
                annotate(comment_count=Count('comments')).
                filter(is_published=True, category__is_published=True,
                       pub_date__lte=timezone.now()).order_by('-pub_date'))
    return queryset


def base_profile_query_set(model_manager=Post.objects, cur_user=None):
    """Базовый запрос с неопубликованными"""
    queryset = (model_manager.all().
                select_related('category', 'location', 'author').
                annotate(comment_count=Count('comments')).
                filter(author=cur_user).order_by('-pub_date'))
    return queryset


# class OnlyAuthorMixin(UserPassesTestMixin):

#     def test_func(self):
#         object = self.get_object()
#         return object.author == self.request.user

class OnlyAuthorOrAdminMixin(UserPassesTestMixin):
    """Только автор и админ"""

    def test_func(self):
        object = self.get_object()
        return (object.author == self.request.user
                or self.request.user.is_superuser)    


class IndexPostsView(TemplateView):
    """Главная страница"""

    model = Post
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        posts = base_query_set()
        page_number = self.request.GET.get('page')
        paginator = Paginator(posts, POST_COUNT_LIMIT)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class CategoryPostsView(ListView):
    """Все публикации в категории"""

    model = Post
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        cur_category = get_object_or_404(
            Category.objects.all().filter(is_published=True,
                                          slug=self.kwargs['category_slug'])
                                          )
        # posts = base_query_set(cur_category.posts.all())
        posts = base_query_set()
        posts = posts.filter(category_id=cur_category)
        page_number = self.request.GET.get('page')
        paginator = Paginator(posts, POST_COUNT_LIMIT)
        page_obj = paginator.get_page(page_number)
        context = super().get_context_data(**kwargs)
        context['page_obj'] = page_obj
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
        form.files = self.request.FILES
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'cur_username': self.request.user.username})


class PostDetailView(DetailView):
    """Детали публикации"""

    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        cur_post = get_object_or_404(Post.objects.all().filter(pk=self.kwargs['pk']))
        if not cur_post.is_published:
            cur_post = get_object_or_404(Post.objects.all().
                                       filter(pk=self.kwargs['pk'],
                                       author=self.request.user))
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (self.object.comments.select_related('author').
                               order_by('created_at'))
        return context
    success_url = reverse_lazy('blog:index')


class PostUpdateView(UpdateView):
    """Редактирование публикации"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        cur_post = get_object_or_404(Post.objects.all().
                                     filter(pk=self.kwargs['pk']))
        if not cur_post.author == self.request.user:
            return redirect(reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['pk']})) 
        form.files = self.request.FILES
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['pk']})


class PostDeleteView(OnlyAuthorOrAdminMixin, DeleteView):
    """Удаление публикации"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs) 
        context['post'] = self.object 
        return context 

    def get_form(self, form_class=None):
        return form_class(**kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'cur_username': self.request.user.username})


class ProfileListView(ListView):
    """Страница пользователя"""

    model = Post
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        user_model = get_user_model()
        cur_user = get_object_or_404(
            user_model.objects.all().
            filter(username=self.kwargs['cur_username'])
        )

        posts = base_profile_query_set(Post.objects.all(), cur_user)
        if not self.request.user == cur_user:
            posts = posts.filter(is_published=True,
                                 category__is_published=True,
                                 pub_date__lte=timezone.now())

        page_number = self.request.GET.get('page')
        paginator = Paginator(posts, POST_COUNT_LIMIT)
        page_obj = paginator.get_page(page_number)
        context = super().get_context_data(**kwargs)
        context['page_obj'] = page_obj
        context['profile'] = cur_user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля"""

    model = User
    form_class = ProfileUpdateForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['request'] = self.request
        if self.request.POST:
            context['form'] = UserUpdateForm(self.request.POST,
                                             instance=self.request.user)
        else:
            context['form'] = UserUpdateForm(instance=self.request.user)
        return context

    success_url = reverse_lazy('blog:index')


class BaseCommentView(LoginRequiredMixin):
    """Комментарий"""

    model = Comment

    def get_success_url(self):  
        return reverse(  
            "blog:post_detail",
            kwargs={'pk': self.object.post.pk}
        )


class CommentCreateView(BaseCommentView, CreateView):
    """Создание комментария"""

    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        cur_post = get_object_or_404(Post.objects.all().filter(pk=self.kwargs['pk']))
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


class CommentUpdateView(BaseCommentView, UpdateView):
    """Редактирование комментария"""

    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Comment.objects.all().
                                 filter(post=self.kwargs['pk'],
                                        pk=self.kwargs['comment_id'],
                                        author=self.request.user)
                                 )


class CommentDeleteView(OnlyAuthorOrAdminMixin, BaseCommentView, DeleteView):
    """Удаление комментария"""

    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Comment.objects.all().
                                 filter(post=self.kwargs['pk'],
                                        pk=self.kwargs['comment_id'])
                                 )

    def get_success_url(self):
        return reverse(  
            "blog:post_detail",
            kwargs={'pk': self.kwargs['pk']}
        )
