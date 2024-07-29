from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from .constants import TITLE_MAX_LENGTH, TITLE_MAX_LENGTH_ADMIN

User = get_user_model()


class PublishedModel(models.Model):
    """Абстрактная модель. Добавляет общие поля"""

    is_published = models.BooleanField(
        verbose_name='Опубликовано', default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(verbose_name='Добавлено',
                                      auto_now=False, auto_now_add=True)

    class Meta:
        abstract = True


class Location(PublishedModel):
    """Местоположения"""

    name = models.CharField(verbose_name='Название места',
                            max_length=TITLE_MAX_LENGTH)

    class Meta:
        """Meta"""

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:TITLE_MAX_LENGTH_ADMIN]


class Category(PublishedModel):
    """Категории"""

    title = models.CharField(verbose_name='Заголовок',
                             max_length=TITLE_MAX_LENGTH)
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        help_text=('Идентификатор страницы для URL; разрешены'
                   ' символы латиницы, цифры, дефис и подчёркивание.'),
        verbose_name='Идентификатор'
    )

    class Meta:
        """Meta"""

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:TITLE_MAX_LENGTH_ADMIN]


class Post(PublishedModel):
    """Публикации"""

    title = models.CharField(verbose_name='Название',
                             max_length=TITLE_MAX_LENGTH)
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем —'
                   ' можно делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    image = models.ImageField('Изображение', upload_to='posts_images',
                              blank=True)

    class Meta:
        """Meta"""

        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:TITLE_MAX_LENGTH_ADMIN]

    def get_absolute_url(self):
        # С помощью функции reverse() возвращаем URL объекта.
        return reverse('post:post_detail', kwargs={'pk': self.pk})   


class Comment(models.Model):
    """Комментарии к публикациям"""

    text = models.TextField('Комментарий')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, 
                             related_name='comments',
                             )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created_at',)
