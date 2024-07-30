from django.db.models import Count
from django.utils import timezone

from .models import Post


def base_query_set(model_manager=Post.objects, in_published_only=True,
                   add_annotate=True):
    """Базовый запрос"""
    queryset = (model_manager.all().
                select_related('category', 'location', 'author').
                order_by('-pub_date'))
    if in_published_only:
        queryset = (queryset.
                    filter(is_published=True,
                           category__is_published=True,
                           pub_date__lte=timezone.now()))
    if add_annotate:
        queryset = queryset.annotate(comment_count=Count('comments'))

    return queryset
