from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название сообщества',
        help_text='Введите название для сообщества'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Короткая метка сообщества',
        help_text='Введите уникальную короткую метку для сообщества'
    )
    description = models.TextField(
        verbose_name='Описание сообщества',
        help_text='Введите краткое описание для сообщества',
    )

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Сообщество к которому относится пост',
        help_text='Выберите сообщество поста'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Выберите изображение для загрузки',
        upload_to='posts/',
        blank=True
    )
    TEMPLATE_FIELDS = (
        'Краткое содержание поста: {text:.15}, '
        'Сообщество: {group}, '
        'Пользователь: {author}, '
        'Дата публикации поста: {pub_date}'
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.TEMPLATE_FIELDS.format(
            text=self.text,
            group=self.group,
            author=self.author.username,
            pub_date=self.pub_date
        )


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост к которому оставлен комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь, который оформил подписку на автора',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор на которого подписались',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
