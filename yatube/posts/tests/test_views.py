from django.test import Client, TestCase
from django.urls import reverse

from yatube.settings import AMOUNT_PAGES, OTHER_PAGES
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


class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Создадим запись в БД
        cls.user = User.objects.create_user(username='Roman')
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
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизированный клиент клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    # Проверка 0: проверка context от post
    def check_post_context(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.id, self.post.id)

    # Проверка : в шаблон передан правильный контекст
    def test_show_correct_context(self):
        urls = [
            INDEX_URL,
            GROUP_LIST_URL,
            PROFILE_URL,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if 'page_obj' in response.context:
                    self.assertEqual(len(response.context['page_obj']), 1)
                    post = response.context['page_obj'][0]
                self.check_post_context(post)

    def test_detail_page_show_correct(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', args=[self.post.pk])
        )
        post = response.context['post']
        self.check_post_context(post)

    def test_new_post_in_another_group(self):
        """Наличие поста в другой группе"""
        self.assertNotIn(
            self.post,
            self.authorized_client.get(
                reverse(
                    'posts:posts_slug',
                    args=[self.group_2.slug])).context['page_obj']
        )

    class PaginatorViewsTest(TestCase):
        @classmethod
        def setUpClass(cls) -> None:
            super().setUpClass()
            # Создадим запись в БД
            cls.user = User.objects.create_user(username='Roman')
            cls.group = Group.objects.create(
                title='Тестовая группа',
                slug='test-slug',
                description='Тестовое описание',
            )
            for i in range(1, 14):
                Post.objects.bulk_create([Post(
                    text=POST_TEXT,
                    author=cls.user,
                    group=cls.group)])

        def setUp(self) -> None:
            # Создаем авторизированный клиент клиент
            self.authorized_client = Client()
            # Авторизуем пользователя
            self.authorized_client.force_login(self.user)

        # Тестирование пажинатора

        def test_paginator_on_pages_have_ten_post(self):
            '''Количество постов на страницах не больше 10 штук.'''
            pages = [
                INDEX_URL,
                GROUP_LIST_URL,
                PROFILE_URL
            ]
            for page in pages:
                with self.subTest(page=page):
                    response = self.client.get(page)
                    self.assertEqual(
                        len(response.context['page_obj'], AMOUNT_PAGES)
                    )
                    response = self.client.get(page + '?page=2')
                    self.assertEqual(
                        len(response.context['page_obj'], OTHER_PAGES)
                    )
