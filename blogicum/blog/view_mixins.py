from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse


from .forms import CommentForm
from .models import Comment


class OnlyAuthorMixin(UserPassesTestMixin):
    """Только автор"""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect(
            reverse_lazy('blog:post_detail',
                         kwargs={'post_id': self.kwargs['post_id']}))


class BaseCommentMixin(LoginRequiredMixin):
    """Комментарий"""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={'post_id': self.object.post.pk}
        )

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, post=self.kwargs['post_id'],
                                 pk=self.kwargs['comment_id'])
