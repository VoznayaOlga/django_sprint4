from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy


class OnlyAuthorMixin(UserPassesTestMixin):
    """Только автор"""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect(
            reverse_lazy('blog:post_detail',
                         kwargs={'post_id': self.kwargs['post_id']}))
