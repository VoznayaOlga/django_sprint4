from django.contrib import admin

from .models import Category, Location, Post, Comment

class CommentInline(admin.TabularInline):
    """Комментарий"""

    model = Comment
    extra = 1
    
class PostAdmin(admin.ModelAdmin):
    """Публикации"""

    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = (
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published'
    )
    inlines = (
        CommentInline,
    )
    search_fields = ('title',)
    list_filter = ('category', 'location')
    list_display_links = ('title',)
    empty_value_display = 'Не задано'


class PostInline(admin.TabularInline):
    """Публикация"""

    model = Post
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    """Категория"""
    
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
    )
 
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
