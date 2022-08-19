import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

USERNAME = 'UserTest'
NON_AUTHOR_USERNAME = 'PostNonAuthor'
GROUP_SLUG = 'test-slug'
GROUP_SLUG_2 = 'test-slug-2'
LOGIN_URL = reverse('users:login') + '?next='
POST_CREATE_URL = reverse('posts:post_create')
USER_URL = reverse('posts:profile', args=[USERNAME])
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOAD_TO = Post.image.field.upload_to


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_non_author_post = User.objects.create_user(
            username=NON_AUTHOR_USERNAME
        )
        cls.group = Group.objects.create(
            title='Тестовое название сообщества',
            slug=GROUP_SLUG,
            description='Тестовое описание сообщества',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовое название сообщества 2',
            slug=GROUP_SLUG_2,
            description='Тестовое описание сообщества 2',
        )
        cls.post = Post.objects.create(
            text='Тестовая запись текста поста',
            author=cls.user,
            group=cls.group,
            image=None
        )
        cls.DETAIL_POST_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.EDIT_POST_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.COMMENT_URL = reverse('posts:add_comment', args=[cls.post.id])
        cls.EDIT_POST_REDIRECT_URL = LOGIN_URL + cls.EDIT_POST_URL
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.another = Client()
        cls.another.force_login(cls.user_non_author_post)

    def setUp(self):
        self.UPLOADED = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        Post.objects.all().delete()
        form_data = {
            'text': 'Тестовый текст формы',
            'group': self.group.id,
            'image': self.UPLOADED
        }
        response = self.author.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, USER_URL)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.all()[0]
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image, f"{UPLOAD_TO}{form_data['image']}")

    def test_post_edit(self):
        """Валидная форма изменяет пост по post_id в базе данных."""
        form_data = {
            'text': 'Изменённый текст поста',
            'group': self.group_2.id,
            'image': self.UPLOADED
        }
        response = self.author.post(
            self.EDIT_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.DETAIL_POST_URL)
        post = response.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.image, f'{UPLOAD_TO}{form_data["image"]}')

    def test_post_create_edit_pages_show_correct_context(self):
        """
        Шаблон post_create и post_edit сформирован с правильным контекстом.
        """
        reverses = [self.EDIT_POST_URL, POST_CREATE_URL]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for revers in reverses:
            response = self.author.get(revers)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_author_comment_creation_form(self):
        """
        Проверка формы создания комментария для авторизованного пользователя
        """
        Comment.objects.all().delete()
        form_data = {'text': 'Тестовый текст формы'}
        response = self.author.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.DETAIL_POST_URL)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.all()[0]
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post.id, self.post.id)

    def test_guest_create_post(self):
        """Проверка возможности гостя создания поста."""
        Post.objects.all().delete()
        form_data = {
            'text': 'Тестовый текст формы',
            'group': self.group.id,
            'image': self.UPLOADED
        }
        self.guest.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_guest_create_comment(self):
        """Проверка возможности гостя создания комментария."""
        Comment.objects.all().delete()
        form_data = {'text': 'Тестовый текст формы'}
        self.guest.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_guest_another_edit_post(self):
        """Проверка возможности гостя, не-автора редактирования поста."""
        form_data = {
            'text': 'Изменённый текст поста автора',
            'group': self.group_2,
            'image': self.UPLOADED,
        }
        CLIENT_URL = (
            (self.another, self.DETAIL_POST_URL),
            (self.guest, self.EDIT_POST_REDIRECT_URL)
        )
        for client, url in CLIENT_URL:
            with self.subTest(client=client, url=url):
                response = client.post(
                    self.EDIT_POST_URL,
                    data=form_data,
                    follow=True
                )
                self.assertRedirects(response, url)
                self.assertEqual(Post.objects.count(), 1)
                self.assertTrue(Post.objects.filter(author=self.post.author))
                self.assertTrue(Post.objects.filter(image=self.post.image))
                self.assertTrue(Post.objects.filter(text=self.post.text))
                self.assertTrue(Post.objects.filter(group=self.post.group))
