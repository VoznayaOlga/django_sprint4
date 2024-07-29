from django.contrib import admin

from .models import Category, Location, Post


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


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
