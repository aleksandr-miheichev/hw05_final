from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def testing_url_addresses_of_pages_available_to_all_users(self):
        """Проверка доступности адреса /author/ и /tech/."""
        templates_url = (
            '/about/author/',
            '/about/tech/',
        )
        for template_url in templates_url:
            response = self.guest_client.get(template_url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def testing_page_urls_using_the_correct_pattern(self):
        """Проверка шаблона для адреса /author/ и /tech/."""
        templates_url = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in templates_url.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_about_page_accessible_by_name(self):
        """
        URL, генерируемый при помощи имени about:author и about:tech, доступен.
        """
        reverses = [reverse('about:author'), reverse('about:tech')]
        for revers in reverses:
            response = self.guest_client.get(revers)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_uses_correct_template(self):
        """При запросе к about:author и about:tech применяются шаблоны
        about/author.html и about/tech.html."""
        templates_url = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for url, template in templates_url.items():
            with self.subTest(url=url):
                response = self.guest_client.get(reverse(url))
                self.assertTemplateUsed(response, template)
