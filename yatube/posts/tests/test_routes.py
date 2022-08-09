from django.test import TestCase
from django.urls import reverse

USERNAME_TEST = 'UserTest'
GROUP_SLUG_TEST = 'test-slug'
POST_ID = 1
DATA = (
    ('index', [], '/'),
    ('group_list', [GROUP_SLUG_TEST], f'/group/{GROUP_SLUG_TEST}/'),
    ('profile', [USERNAME_TEST], f'/profile/{USERNAME_TEST}/'),
    ('post_detail', [POST_ID], f'/posts/{POST_ID}/'),
    ('post_create', [], '/create/'),
    ('post_edit', [POST_ID], f'/posts/{POST_ID}/edit/'),
    ('add_comment', [POST_ID], f'/posts/{POST_ID}/comment/'),
    ('follow_index', [], '/follow/'),
    ('profile_follow', [USERNAME_TEST], f'/profile/{USERNAME_TEST}/follow/'),
    (
        'profile_unfollow',
        [USERNAME_TEST],
        f'/profile/{USERNAME_TEST}/unfollow/'
    ),
)


class PostModelTest(TestCase):
    def test_routes(self):
        """Расчёты urls дают ожидаемые явные urls."""
        for route, args, explicit_url in DATA:
            with self.subTest(explicit_url=explicit_url):
                self.assertEqual(
                    reverse(f'posts:{route}', args=args),
                    explicit_url
                )
