from django.test import TestCase

from ..models import Group, Post, User

USERNAME_TEST = 'UserTest'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME_TEST)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        correct_title_group = self.group.title
        correct_text_post = Post.TEMPLATE_FIELDS.format(
            text=self.post.text,
            group=self.post.group,
            author=self.post.author.username,
            pub_date=self.post.pub_date
        )
        self.assertEqual(correct_title_group, str(self.group))
        self.assertEqual(correct_text_post, str(self.post))

    def test_post_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата создания',
            'author': 'Автор поста',
            'group': 'Сообщество к которому относится пост',
            'image': 'Изображение'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_post_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите сообщество поста',
            'image': 'Выберите изображение для загрузки'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text,
                    expected_value
                )

    def test_group_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'title': 'Название сообщества',
            'slug': 'Короткая метка сообщества',
            'description': 'Описание сообщества',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_group_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'title': 'Введите название для сообщества',
            'slug': 'Введите уникальную короткую метку для сообщества',
            'description': 'Введите краткое описание для сообщества',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).help_text,
                    expected_value
                )
