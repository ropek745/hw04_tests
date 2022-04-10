from django.test import TestCase
from django.urls import reverse

ID = 5
USERNAME = 'Roman'
SLUG = 'test-slug'


class TestRoutes(TestCase):
    def test_routes(self):
        routes = [
            ['/', 'index', []],
            ['/create/', 'post_create', []],
            [f'/group/{SLUG}/', 'posts_slug', [SLUG]],
            [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
            [f'/posts/{ID}/', 'post_detail', [ID]],
            [f'/posts/{ID}/edit/', 'post_edit', [ID]]
        ]
        for url, route, args in routes:
            with self.subTest(url=url, route=route, args=args):
                result = reverse(f'posts:{route}', args=args)
                self.assertEqual(url, result)
