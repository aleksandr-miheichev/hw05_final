from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='UserTest')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def testing_url_addresses_of_pages_available_to_all_users(self):
        """Страницы доступные любому пользователю сайта."""
        templates_url = (
            '/auth/signup/',
            '/auth/logout/',
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/<uidb64>/<token>/',
            '/auth/reset/done/',
        )
        for template_url in templates_url:
            response = self.guest_client.get(template_url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def testing_url_addresses_of_pages_available_to_an_authorized_users(self):
        """Страницы /auth/password_change/ и /auth/password_change/done/
        доступные только авторизованному пользователю."""
        templates_url = (
            '/auth/password_change/',
            '/auth/password_change/done/',
        )
        for template_url in templates_url:
            response = self.authorized_client.get(template_url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def testing_page_urls_for_an_unauthorized_user_with_a_redirect(self):
        """
        Страницы /auth/password_change/ и /auth/password_change/done/
        перенаправят анонимного пользователя на страницу логина.
        """
        templates_url = (
            '/auth/password_change/',
            '/auth/password_change/done/',
        )
        for template_url in templates_url:
            response = self.guest_client.get(template_url, follow=True)
            self.assertRedirects(response, f'/auth/login/?next={template_url}')

    def testing_page_urls_using_the_correct_pattern(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url = {
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/': (
                'users/password_reset_confirm.html'
            ),
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for url, template in templates_url.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
