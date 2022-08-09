from http.client import FOUND, NOT_FOUND, OK

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

POST_AUTHOR_USERNAME_TEST = 'PostAuthor'
POST_NON_AUTHOR_USERNAME_TEST = 'PostNonAuthor'
GROUP_SLUG_TEST = 'test-slug'
MAIN_PAGE_URL = reverse('posts:index')
POST_CREATE_URL = reverse('posts:post_create')
LOGIN_PAGE_URL = reverse('users:login') + '?next='
UNEXISTING_PAGE = '/unexisting_page/'
USER_PAGE_URL = reverse('posts:profile', args=[POST_AUTHOR_USERNAME_TEST])
COMMUNITY_PAGE_URL = reverse('posts:group_list', args=[GROUP_SLUG_TEST])


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author_post = User.objects.create_user(
            username=POST_AUTHOR_USERNAME_TEST
        )
        cls.user_non_author_post = User.objects.create_user(
            username=POST_NON_AUTHOR_USERNAME_TEST
        )
        cls.group = Group.objects.create(
            title='Тестовое название сообщества',
            slug=GROUP_SLUG_TEST,
            description='Тестовое описание сообщества',
        )
        cls.post = Post.objects.create(
            text='Тестовая запись текста поста',
            author=cls.user_author_post,
            group=cls.group
        )
        cls.DETAIL_POST_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.EDIT_POST_URL = reverse('posts:post_edit', args=[cls.post.id])

    def setUp(self):
        self.guest = Client()
        self.author = Client()
        self.author.force_login(self.user_author_post)
        self.another = Client()
        self.another.force_login(self.user_non_author_post)

    def test_checking_http_status_of_pages_for_different_user_groups(self):
        """Проверка http статуса страниц для разных групп пользователей."""
        data = (
            (MAIN_PAGE_URL, self.guest, OK),
            (COMMUNITY_PAGE_URL, self.guest, OK),
            (USER_PAGE_URL, self.guest, OK),
            (self.DETAIL_POST_URL, self.guest, OK),
            (UNEXISTING_PAGE, self.guest, NOT_FOUND),
            (POST_CREATE_URL, self.guest, FOUND),
            (POST_CREATE_URL, self.author, OK),
            (self.EDIT_POST_URL, self.guest, FOUND),
            (self.EDIT_POST_URL, self.author, OK),
            (self.EDIT_POST_URL, self.another, FOUND)
        )
        for url, client, http_status in data:
            with self.subTest(url=(client.get(url), http_status)):
                self.assertEqual(client.get(url).status_code, http_status)

    def test_how_different_clients_interact_with_page_templates(self):
        data = (
            (POST_CREATE_URL, self.guest, LOGIN_PAGE_URL + POST_CREATE_URL),
            (
                self.EDIT_POST_URL,
                self.guest,
                LOGIN_PAGE_URL + self.EDIT_POST_URL
            ),
            (self.EDIT_POST_URL, self.another, self.DETAIL_POST_URL),
        )
        for url, client, redirect_url in data:
            with self.subTest(template_url=url):
                self.assertRedirects(
                    client.get(url, follow=True),
                    redirect_url
                )

    def test_page_urls_using_the_correct_pattern(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url = {
            MAIN_PAGE_URL: 'posts/index.html',
            COMMUNITY_PAGE_URL: 'posts/group_list.html',
            USER_PAGE_URL: 'posts/profile.html',
            self.DETAIL_POST_URL: 'posts/post_detail.html',
            self.EDIT_POST_URL: 'posts/post_create.html',
            POST_CREATE_URL: 'posts/post_create.html',
        }
        for url, template in templates_url.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.author.get(url),
                    template
                )

    def test_404_page(self):
        """Проверяем, что страница 404 отдаёт кастомный шаблон"""
        self.assertTemplateUsed(
            self.guest.get(UNEXISTING_PAGE),
            'core/404.html'
        )
