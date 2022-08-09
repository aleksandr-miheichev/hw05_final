from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='UserTest',
            email='email_test@gmail.com',
            last_name='last_name_test',
            first_name='first_name_test',
        )

    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        """Валидная форма создает нового пользователя в User."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'first_name_test_1',
            'last_name': 'last_name_test_1',
            'username': 'UserTest_1',
            'email': 'email_test_1@gmail.com',
            'password1': 'XPzekwfub8GmL!P',
            'password2': 'XPzekwfub8GmL!P'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(User.objects.filter(
            first_name='first_name_test_1',
            last_name='last_name_test_1',
            username='UserTest_1',
            email='email_test_1@gmail.com',
        ).exists())
