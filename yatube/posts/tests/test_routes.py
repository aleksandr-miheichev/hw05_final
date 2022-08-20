from django.test import TestCase
from django.urls import reverse

from posts.urls import app_name

USERNAME = 'UserTest'
GROUP_SLUG = 'test-slug'
POST_ID = 1
DATA = (
    ('index', [], '/'),
    ('group_list', [GROUP_SLUG], f'/group/{GROUP_SLUG}/'),
    ('profile', [USERNAME], f'/profile/{USERNAME}/'),
    ('post_detail', [POST_ID], f'/posts/{POST_ID}/'),
    ('post_create', [], '/create/'),
    ('post_edit', [POST_ID], f'/posts/{POST_ID}/edit/'),
    ('add_comment', [POST_ID], f'/posts/{POST_ID}/comment/'),
    ('follow_index', [], '/follow/'),
    ('profile_follow', [USERNAME], f'/profile/{USERNAME}/follow/'),
    ('profile_unfollow', [USERNAME], f'/profile/{USERNAME}/unfollow/'),
)


class PostModelTest(TestCase):
    def test_routes(self):
        """Расчёты urls дают ожидаемые явные urls."""
        for route, args, explicit_url in DATA:
            with self.subTest(explicit_url=explicit_url):
                self.assertEqual(
                    reverse(f'{app_name}:{route}', args=args),
                    explicit_url
                )
