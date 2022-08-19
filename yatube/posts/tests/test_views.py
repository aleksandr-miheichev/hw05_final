import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User
from ..settings import POSTS_PER_PAGE

USERNAME = 'UserTest'
AUTHUSERNAME = 'Follower'
NON_AUTHOR_USERNAME = 'PostNonAuthor'
GROUP_SLUG = 'test-slug'
GROUP_SLUG_2 = 'test-slug-2'
MAIN_URL = reverse('posts:index')
MAIN_URL_2 = MAIN_URL + '?page=2'
POST_CREATE_URL = reverse('posts:post_create')
USER_URL = reverse('posts:profile', args=[USERNAME])
USER_URL_2 = USER_URL + '?page=2'
COMMUNITY_URL = reverse('posts:group_list', args=[GROUP_SLUG])
COMMUNITY_URL_2 = COMMUNITY_URL + '?page=2'
COMMUNITY_URL_SLUG_2 = reverse(
    'posts:group_list',
    args=[GROUP_SLUG_2]
)
FOLLOW_URL = reverse('posts:follow_index')
FOLLOW_URL_2 = FOLLOW_URL + '?page=2'
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])
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
        cls.user = User.objects.create_user(username=USERNAME)
        cls.follower = User.objects.create_user(username=AUTHUSERNAME)
        cls.user_non_author_post = User.objects.create_user(
            username=NON_AUTHOR_USERNAME
        )
        cls.group1 = Group.objects.create(
            title='Тестовое название сообщества',
            slug=GROUP_SLUG,
            description='Тестовое описание сообщества',
        )
        cls.group2 = Group.objects.create(
            title='Тестовое название сообщества 2',
            slug=GROUP_SLUG_2,
            description='Тестовое описание сообщества 2',
        )
        cls.post = Post.objects.create(
            text='Тестовая запись текста поста',
            author=cls.user,
            group=cls.group1,
            image=UPLOADED
        )
        cls.DETAIL_POST_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.subscriber = Client()
        cls.subscriber.force_login(cls.follower)
        cls.another = Client()
        cls.another.force_login(cls.user_non_author_post)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_page_show_correct_context(self):
        """Страницы сформированы с правильным контекстом."""
        Follow.objects.all().delete()
        if self.user != self.follower:
            Follow.objects.create(user=self.follower, author=self.user)
        data = (
            (self.DETAIL_POST_URL, 'post'),
            (MAIN_URL, 'page_obj'),
            (USER_URL, 'page_obj'),
            (COMMUNITY_URL, 'page_obj'),
            (FOLLOW_URL, 'page_obj')
        )
        for page_url, posts_context in data:
            response = self.subscriber.get(page_url)
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
        """group_list сформирован с правильным контекстом"""
        response = self.guest.get(COMMUNITY_URL)
        group = response.context['group']
        self.assertEqual(group.description, self.group1.description)
        self.assertEqual(group, self.group1)
        self.assertEqual(group.slug, self.group1.slug)
        self.assertEqual(group.title, self.group1.title)

    def test_post_another_group(self):
        """Пост не попал в группу, для которой не был предназначен"""
        Follow.objects.all().delete()
        if self.user != self.follower:
            Follow.objects.create(user=self.follower, author=self.user)
        for url in [COMMUNITY_URL_SLUG_2, FOLLOW_URL]:
            with self.subTest(url=url):
                self.assertNotIn(
                    self.post,
                    self.another.get(url).context['page_obj']
                )

    def test_author_context_profile(self):
        """Страница профиля автора с правильным контекстом"""
        self.assertEqual(
            self.user,
            self.guest.get(USER_URL).context['author']
        )

    def test_cache_index_page(self):
        """Проверка кеширования главной страницы"""
        response_first = self.author.get(MAIN_URL)
        Post.objects.all().delete()
        response_second = self.author.get(MAIN_URL)
        self.assertEqual(response_second.content, response_first.content)
        cache.clear()
        response_third = self.author.get(MAIN_URL)
        self.assertNotEqual(response_third.content, response_second.content)

    def test_subscription_to_other_users_of_an_authorized_user(self):
        """Тест возможности подписки на других пользователей авторизованного
         пользователя."""
        Follow.objects.all().delete()
        self.subscriber.get(PROFILE_FOLLOW_URL)
        self.assertTrue(
            Follow.objects.get(user=self.follower, author=self.user)
        )

    def test_unsubscribing_from_a_favorite_author_by_an_authorized_user(self):
        """Тест возможности отписки от понравившегося автора авторизованным
        пользователем."""
        Follow.objects.all().delete()
        self.assertTrue(
            Follow.objects.create(user=self.follower, author=self.user)
        )
        self.subscriber.get(PROFILE_UNFOLLOW_URL)
        self.assertFalse(
            Follow.objects.filter(user=self.follower, author=self.user)
        )

    def test_paginator_page_displays_set_number_of_posts(self):
        """
        На страницах паджинатора выводится установленное количество постов
        """
        Post.objects.all().delete()
        PAGE_URL_POST_COUNT = (
            (MAIN_URL, POSTS_PER_PAGE),
            (COMMUNITY_URL, POSTS_PER_PAGE),
            (USER_URL, POSTS_PER_PAGE),
            (FOLLOW_URL, POSTS_PER_PAGE),
            (FOLLOW_URL_2, 1),
            (MAIN_URL_2, 1),
            (COMMUNITY_URL_2, 1),
            (USER_URL_2, 1),
        )
        Post.objects.bulk_create(Post(
            text=f'Тестовая запись текста {i} поста',
            author=self.user,
            group=self.group1,
            image=UPLOADED
        ) for i in range(POSTS_PER_PAGE + 1))
        if self.user != self.follower:
            Follow.objects.create(user=self.follower, author=self.user)
        for page_url, post_count in PAGE_URL_POST_COUNT:
            with self.subTest(page_url=page_url):
                response = self.subscriber.get(page_url)
                posts = response.context['page_obj']
                self.assertEqual(len(posts), post_count)
