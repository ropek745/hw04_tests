from django.test import TestCase
from django.urls import reverse

ID = 5
USERNAME = 'Roman'
SLUG = 'test-slug'

INDEX_ROUTE = ['/', 'index', []]
GROUP_LIST_ROUTE = [f'/group/{SLUG}/', 'posts_slug', [SLUG]]
CREATE_ROUTE = ['/create/', 'post_create', []]
PROFILE_ROUTE = [f'/profile/{USERNAME}/', 'profile', [USERNAME]]
POST_DETAIL_ROUTE = [f'/posts/{ID}/', 'post_detail', [ID]]
POST_EDIT_ROUTE = [f'/posts/{ID}/edit/', 'post_edit', [ID]]


class TestRoutes(TestCase):
    def test_routes(self):
        routes = [
            INDEX_ROUTE,
            CREATE_ROUTE,
            GROUP_LIST_ROUTE,
            PROFILE_ROUTE,
            POST_DETAIL_ROUTE,
            POST_EDIT_ROUTE
        ]
        for url, route, args in routes:
            with self.subTest(url=url, route=route, args=args):
                result = reverse(f'posts:{route}', args=args)
                self.assertEqual(url, result)
