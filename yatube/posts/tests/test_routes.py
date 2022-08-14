from django.test import TestCase
from django.urls import reverse

USERNAME = 'UserTest'
GROUP_SLUG = 'test-slug'
POST_ID = 1
DATA = (
    ('posts:index', [], '/'),
    ('posts:group_list', [GROUP_SLUG], f'/group/{GROUP_SLUG}/'),
    ('posts:profile', [USERNAME], f'/profile/{USERNAME}/'),
    ('posts:post_detail', [POST_ID], f'/posts/{POST_ID}/'),
    ('posts:post_create', [], '/create/'),
    ('posts:post_edit', [POST_ID], f'/posts/{POST_ID}/edit/'),
    ('posts:add_comment', [POST_ID], f'/posts/{POST_ID}/comment/'),
    ('posts:follow_index', [], '/follow/'),
    ('posts:profile_follow', [USERNAME], f'/profile/{USERNAME}/follow/'),
    ('posts:profile_unfollow', [USERNAME], f'/profile/{USERNAME}/unfollow/'),
)


class PostModelTest(TestCase):
    def test_routes(self):
        """Расчёты urls дают ожидаемые явные urls."""
        for route, args, explicit_url in DATA:
            with self.subTest(explicit_url=explicit_url):
                self.assertEqual(reverse(route, args=args), explicit_url)
