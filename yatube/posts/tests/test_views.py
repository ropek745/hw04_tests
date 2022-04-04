from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsPagesTest(TestCase):
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовая пост',
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизированный клиент клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.group_2 = Group.objects.create(
            title='Группа-2',
            slug='test-2',
            description='Тестовое описание'
        )

    # Проверка 0: проверка context от post
    def check_post_context(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)

    # Проверка 1: view-классы используют ожидаемые HTML-шаблоны

    def templates_pages_names(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:posts_slug', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
        }
        for template, reverse_name in templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка 2: в шаблон передан правильный контекст
    def test_show_correct_context(self):
        urls = [
            reverse('posts:index'),
            reverse('posts:posts_slug', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user]),
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

    def test_create_post_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for field, expected_value in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected_value)

    def test_edit_post_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit', args=[self.post.pk])
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for field, expected_value in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected_value)

    def test_create_post_group_show(self):
        """
        Проверяем, что, указывая группу при создании поста,
        пост появится на главной странице, странице
        выбранной группы и в профайле пользователя.
        """
        url_list = [
            reverse('posts:index'),
            reverse('posts:posts_slug', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user]),
        ]
        for url in url_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if 'page_obj' in response.context:
                    self.assertEqual(len(response.context['page_obj']), 1)
                    post = response.context['page_obj'][0]
                else:
                    post = response.context['post']
                self.assertEqual(post.group, self.post.group)

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
            cls.post = (
                Post.objects.create(
                    text=f'Test text {number}',
                    author=cls.user,
                    group=cls.group,
                )
                for number in range(1, 14)
            )

        def setUp(self) -> None:
            # Создаем авторизированный клиент клиент
            self.authorized_client = Client()
            # Авторизуем пользователя
            self.authorized_client.force_login(self.user)

        # Тестирование пажинатора

        def test_paginator_on_pages_have_ten_post(self):
            '''Количество постов на страницах не больше 10 штук.'''
            pages = [
                reverse('index'),
                reverse('posts_slug', args=[self.group.slug]),
                reverse('profile', args=[self.user])
            ]

            for page in pages:
                with self.subTest(page=page):
                    response = self.client.get(page)
                    self.assertEqual(
                        len(response.context['page_obj'], 10)
                    )
                    response = self.client.get(page + '?page=2')
                    self.assertEqual(
                        len(response.context['page_obj'], 3)
                    )
