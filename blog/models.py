from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count


class PostQuerySet(models.QuerySet):

    def popular(self, field):
        popular = self.prefetch_related('author', 'tags').annotate(Count(field)).order_by(f'-{field}__count')
        return popular

    def fetch_with_comments_count(self, field, chart_length=5):
        '''
        Add attribute 'comments_count'
        :param field: field for count and  sort for  result
        :param chart_length: the length of slice
        :return: sorted list of posts with length pointed in argument
        '''
        most_popular_posts = self.popular(field)[:chart_length]
        posts_comments = self.annotate(Count('comments'))
        for post in most_popular_posts:
            for post_comments in posts_comments:
                if post_comments.pk == post.pk:
                    post.comments__count = post_comments.comments__count
                    break

        return most_popular_posts



class TagQuerySet(models.QuerySet):

    def popular(self, field):
        popular = self.annotate(Count(field)).order_by(f'-{field}__count')
        return popular


class Post(models.Model):
    objects = PostQuerySet.as_manager()

    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Tag(models.Model):
    objects = TagQuerySet.as_manager()
    title = models.CharField('Тег', max_length=20, unique=True)

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        verbose_name='Пост, к которому написан', related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
