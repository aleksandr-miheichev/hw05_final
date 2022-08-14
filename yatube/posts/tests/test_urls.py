from http.client import FOUND, NOT_FOUND, OK

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

AUTHOR_USERNAME = 'PostAuthor'
NON_AUTHOR_USERNAME = 'PostNonAuthor'
GROUP_SLUG = 'test-slug'
MAIN_PAGE_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
LOGIN_PAGE_URL = reverse('users:login') + '?next='
CREATE_PAGE_REDIRECT_URL = LOGIN_PAGE_URL + CREATE_URL
UNEXISTING_PAGE = '/unexisting_page/'
USER_PAGE_URL = reverse('posts:profile', args=[AUTHOR_USERNAME])
COMMUNITY_PAGE_URL = reverse('posts:group_list', args=[GROUP_SLUG])
PROFILE_FOLLOW_URL = reverse(
    'posts:profile_follow',
    args=[AUTHOR_USERNAME]
)
PROFILE_FOLLOW_REDIRECT_URL = LOGIN_PAGE_URL + PROFILE_FOLLOW_URL
PROFILE_UNFOLLOW_URL = reverse(
    'posts:profile_unfollow',
    args=[AUTHOR_USERNAME]
)
PROFILE_UNFOLLOW_REDIRECT_URL = LOGIN_PAGE_URL + PROFILE_UNFOLLOW_URL
FOLLOW_URL = reverse('posts:follow_index')


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author_post = User.objects.create_user(
            username=AUTHOR_USERNAME
        )
        cls.user_non_author_post = User.objects.create_user(
            username=NON_AUTHOR_USERNAME
        )
        cls.group = Group.objects.create(
            title='Тестовое название сообщества',
            slug=GROUP_SLUG,
            description='Тестовое описание сообщества',
        )
        cls.post = Post.objects.create(
            text='Тестовая запись текста поста',
            author=cls.user_author_post,
            group=cls.group
        )
        cls.DETAIL_POST_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.EDIT_POST_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.COMMENT_URL = reverse('posts:add_comment', args=[cls.post.id])
        cls.EDIT_POST_REDIRECT_URL = LOGIN_PAGE_URL + cls.EDIT_POST_URL
        cls.COMMENT_REDIRECT_URL = LOGIN_PAGE_URL + cls.COMMENT_URL
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user_author_post)
        cls.another = Client()
        cls.another.force_login(cls.user_non_author_post)

    def test_checking_http_status_of_pages_for_different_user_groups(self):
        """Проверка http статуса страниц для разных групп пользователей."""
        data = (
            (MAIN_PAGE_URL, self.guest, OK),
            (COMMUNITY_PAGE_URL, self.guest, OK),
            (USER_PAGE_URL, self.guest, OK),
            (self.DETAIL_POST_URL, self.guest, OK),
            (UNEXISTING_PAGE, self.guest, NOT_FOUND),
            (CREATE_URL, self.guest, FOUND),
            (CREATE_URL, self.author, OK),
            (self.EDIT_POST_URL, self.guest, FOUND),
            (self.EDIT_POST_URL, self.author, OK),
            (self.EDIT_POST_URL, self.another, FOUND),
            (PROFILE_FOLLOW_URL, self.guest, FOUND),
            (PROFILE_UNFOLLOW_URL, self.guest, FOUND),
            (self.COMMENT_URL, self.guest, FOUND),
        )
        for url, client, http_status in data:
            with self.subTest(url=url, client=client, http_status=http_status):
                self.assertEqual(client.get(url).status_code, http_status)

    def test_correct_pages_redirect(self):
        data = (
            (CREATE_URL, self.guest, CREATE_PAGE_REDIRECT_URL),
            (self.EDIT_POST_URL, self.guest, self.EDIT_POST_REDIRECT_URL),
            (self.EDIT_POST_URL, self.another, self.DETAIL_POST_URL),
            (self.COMMENT_URL, self.guest, self.COMMENT_REDIRECT_URL),
            (PROFILE_FOLLOW_URL, self.guest, PROFILE_FOLLOW_REDIRECT_URL),
            (PROFILE_FOLLOW_URL, self.author, USER_PAGE_URL),
            (PROFILE_UNFOLLOW_URL, self.guest, PROFILE_UNFOLLOW_REDIRECT_URL),
        )
        for url, client, redirect_url in data:
            with self.subTest(url=url, redirect_url=redirect_url):
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
            CREATE_URL: 'posts/post_create.html',
            UNEXISTING_PAGE: 'core/404.html',
            FOLLOW_URL: 'posts/follow.html'
        }
        for url, template in templates_url.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.author.get(url),
                    template
                )
