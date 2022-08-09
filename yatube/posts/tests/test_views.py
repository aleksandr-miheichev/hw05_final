import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User
from ..settings import POSTS_PER_PAGE

USERNAME_TEST = 'UserTest'
AUTHUSERNAME_TEST = 'Follower'
GROUP_SLUG_TEST = 'test-slug'
GROUP_SLUG_TEST_2 = 'test-slug-2'
MAIN_PAGE_URL = reverse('posts:index')
MAIN_PAGE_2_URL = reverse('posts:index') + '?page=2'
POST_CREATE_URL = reverse('posts:post_create')
USER_PAGE_URL = reverse('posts:profile', args=[USERNAME_TEST])
USER_PAGE_URL_2 = reverse('posts:profile', args=[USERNAME_TEST]) + '?page=2'
COMMUNITY_PAGE_URL = reverse('posts:group_list', args=[GROUP_SLUG_TEST])
COMMUNITY_PAGE_2_URL = (reverse('posts:group_list', args=[GROUP_SLUG_TEST])
                        + '?page=2')
COMMUNITY_PAGE_URL_SLUG_2 = reverse(
    'posts:group_list',
    args=[GROUP_SLUG_TEST_2]
)
FOLLOW_PAGE = reverse('posts:follow_index')
PAGE_URL_POST_COUNT = (
    (MAIN_PAGE_URL, POSTS_PER_PAGE),
    (COMMUNITY_PAGE_URL, POSTS_PER_PAGE),
    (USER_PAGE_URL, POSTS_PER_PAGE),
    (MAIN_PAGE_2_URL, 1),
    (COMMUNITY_PAGE_2_URL, 1),
    (USER_PAGE_URL_2, 1),
)
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME_TEST)
        cls.follower = User.objects.create_user(
            username=AUTHUSERNAME_TEST
        )
        cls.group1 = Group.objects.create(
            title='Тестовое название сообщества',
            slug=GROUP_SLUG_TEST,
            description='Тестовое описание сообщества',
        )
        cls.group2 = Group.objects.create(
            title='Тестовое название сообщества 2',
            slug=GROUP_SLUG_TEST_2,
            description='Тестовое описание сообщества 2',
        )
        cls.post = Post.objects.create(
            text='Тестовая запись текста поста',
            author=cls.user,
            group=cls.group1,
            image=UPLOADED
        )
        cls.DETAIL_POST_URL = reverse('posts:post_detail', args=[cls.post.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest = Client()
        self.author = Client()
        self.author.force_login(self.user)
        self.subscriber = Client()
        self.subscriber.force_login(self.follower)

    def test_template_page_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        data = (
            (self.DETAIL_POST_URL, 'post'),
            (MAIN_PAGE_URL, 'page_obj'),
            (USER_PAGE_URL, 'page_obj'),
            (COMMUNITY_PAGE_URL, 'page_obj')
        )
        for page_url, posts_context in data:
            response = self.guest.get(page_url)
            if posts_context == 'post':
                post = response.context[posts_context]
            else:
                self.assertEqual(len(response.context[posts_context]), 1)
                post = response.context[posts_context][0]
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.image, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.guest.get(COMMUNITY_PAGE_URL)
        group = response.context['group']
        self.assertEqual(group.description, self.group1.description)
        self.assertEqual(group, self.group1)
        self.assertEqual(group.slug, self.group1.slug)
        self.assertEqual(group.id, self.group1.id)

    def test_post_another_group(self):
        """Пост не попал в группу, для которой не был предназначен"""
        self.assertNotIn(
            self.post,
            self.guest.get(COMMUNITY_PAGE_URL_SLUG_2).context['page_obj']
        )

    def test_author_context_profile(self):
        """Страница профиля автора с правильным контекстом"""
        self.assertEqual(
            self.user,
            self.guest.get(USER_PAGE_URL).context['author']
        )

    def test_cache_index_page(self):
        """Проверка кеширования главной страницы"""
        Post.objects.all().delete()
        Post.objects.create(
            text=self.post.text,
            author=self.user,
            image=UPLOADED,
            group=self.group1
        )
        response_first = self.author.get(MAIN_PAGE_URL)
        self.assertEqual(Post.objects.count(), 1)
        cache.clear()
        response_second = self.author.get(MAIN_PAGE_URL)
        self.assertNotEqual(response_first.content, response_second.content)

    def test_subscription_to_other_users_of_an_authorized_user(self):
        """Тест возможности подписки на других пользователей авторизованного
         пользователя."""
        Follow.objects.all().delete()
        if self.user != self.follower:
            Follow.objects.create(user=self.follower, author=self.user)
        self.assertTrue(Follow.objects.filter(
            user=self.follower,
            author=self.user
        ).exists())

    def test_unsubscribing_from_a_favorite_author_by_an_authorized_user(self):
        """Тест возможности отписки от понравившегося автора авторизованным
        пользователем."""
        if self.user != self.follower:
            Follow.objects.create(user=self.follower, author=self.user)
        if self.assertTrue(Follow.objects.filter(
            user=self.follower,
            author=self.user
        ).exists()):
            Follow.objects.filter(
                user=self.follower,
                author=self.user
            ).delete()
            self.assertFalse(Follow.objects.filter(
                user=self.follower,
                author=self.user
            ).exists())

    def test_of_the_appearance_of_a_new_entry_by_a_favorite_author(self):
        """Тест появления новой записи любимого автора."""
        Post.objects.all().delete()
        Follow.objects.all().delete()
        if self.user != self.follower:
            Follow.objects.create(user=self.follower, author=self.user)
        post = Post.objects.create(text=self.post.text, author=self.user)
        response = self.subscriber.get(FOLLOW_PAGE)
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].text, post.text)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME_TEST)
        cls.group = Group.objects.create(
            title='Тестовое название сообщества',
            slug=GROUP_SLUG_TEST,
            description='Тестовое описание сообщества',
        )

    def setUp(self):
        self.guest = Client()

    def test_paginator_page_displays_set_number_of_posts(self):
        """
        На страницах паджинатора выводится установленное количество постов
        """
        Post.objects.bulk_create(Post(
            text=f'Тестовая запись текста {i} поста',
            author=self.user,
            group=self.group,
            image=UPLOADED
        ) for i in range(POSTS_PER_PAGE + 1))
        for page_url, post_count in PAGE_URL_POST_COUNT:
            with self.subTest(page_url=page_url):
                response = self.client.get(page_url)
                posts = response.context['page_obj']
                self.assertEqual(len(posts), post_count)
