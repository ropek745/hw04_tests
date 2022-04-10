from django.test import Client, TestCase
from django.urls import reverse

from yatube.settings import PAGINATOR_COUNT
from posts.models import Group, Post, User

GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_TITLE_NEW = 'Группа-2'
GROUP_SLUG_NEW = 'test-2'
GROUP_DESCRIPTION_NEW = 'новая группа'
POST_TEXT = 'I love django tests'
USERNAME = 'Roma'

INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:posts_slug', args=[GROUP_SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
GROUP_LIST_URL_2 = reverse('posts:posts_slug', args=[GROUP_SLUG_NEW])
OTHER_PAGES = 4
NEXT_PAGE = '?page=2'


class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Создадим запись в БД
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.group_2 = Group.objects.create(
            title=GROUP_TITLE_NEW,
            slug=GROUP_SLUG_NEW,
            description=GROUP_DESCRIPTION_NEW
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post_context(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.id, self.post.id)

    def test_show_correct_context(self):
        urls = [
            INDEX_URL,
            GROUP_LIST_URL,
            PROFILE_URL,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context['page_obj']), 1)
                post = response.context['page_obj'][0]
                self.check_post_context(post)

    def test_detail_page_show_correct(self):
        response = self.authorized_client.get(self.POST_DETAIL_URL)
        self.check_post_context(response.context['post'])

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(self.user, response.context['author'])

    def test_group_list_show_correct_context(self):
        response = self.authorized_client.get(GROUP_LIST_URL)
        self.assertEqual(self.group, response.context['group'])
        self.assertEqual(self.group.title, GROUP_TITLE)
        self.assertEqual(self.group.slug, GROUP_SLUG)
        self.assertEqual(self.group.description, GROUP_DESCRIPTION)

    def test_new_post_in_another_group(self):
        """Наличие поста в другой группе"""
        self.assertNotIn(
            self.post,
            self.authorized_client.get(GROUP_LIST_URL_2).context['page_obj'])

    class PaginatorViewsTest(TestCase):
        @classmethod
        def setUpClass(cls) -> None:
            super().setUpClass()
            # Создадим запись в БД
            cls.user = User.objects.create_user(username=USERNAME)
            cls.group = Group.objects.create(
                title=GROUP_TITLE,
                slug=GROUP_SLUG,
                description=GROUP_DESCRIPTION,
            )
            Post.objects.bulk_create(
                Post(text=f'Post {i}', author=cls.user, group=cls.group)
                for i in range(PAGINATOR_COUNT + OTHER_PAGES)
            )

        def setUp(self) -> None:
            self.authorized_client = Client()
            self.authorized_client.force_login(self.user)

        def test_paginator_on_pages_have_ten_post(self):
            '''Количество постов на страницах не больше 10 штук.'''
            urls = [
                [INDEX_URL, PAGINATOR_COUNT],
                [GROUP_LIST_URL, PAGINATOR_COUNT],
                [PROFILE_URL, PAGINATOR_COUNT]
                [INDEX_URL + NEXT_PAGE, OTHER_PAGES],
                [GROUP_LIST_URL + NEXT_PAGE, OTHER_PAGES],
                [PROFILE_URL + NEXT_PAGE, OTHER_PAGES]
            ]
            for url, page_count in urls:
                with self.subTest(url=url):
                    response = self.client.get(url)
                    self.assertEqual(
                        len(response.context['page_obj'], page_count)
                    )
