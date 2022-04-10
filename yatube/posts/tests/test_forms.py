from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'

GROUP_TITLE_NEW = 'Новая тестовая группа'
GROUP_SLUG_NEW = 'test-slug-new'
GROUP_DESCRIPTION_NEW = 'Новое тестовое описание'



CREATE_URL = reverse('posts:post_create')

POST_TEXT = 'Текстовая пост'
NEW_POST_TEXT = 'Новый текст'

USERNAME = 'Roman'

class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.group_new = Group.objects.create(
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
        cls.PROFILE_URL = reverse('posts:profile', args=[cls.user])


    def setUp(self):
        # Создаем неавторизованный клиент
        self.authorized_client = Client()
        # Авторизуем клиента
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        Post.objects.all().delete
        posts_count = Post.objects.count()
        form_data = {
            'text': POST_TEXT,
            'group': self.group
        }
        response = self.authorized_client.post(
            CREATE_URL,
            data=form_data,
            follow=True
        )
        post = Post.objects.get()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_edit(self):
        # Создаём форму
        form_data = {
            'text': NEW_POST_TEXT,
            'group': self.group_new.id
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        post = response.context.get('post')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.post.author)
        self.assertRedirects(response, self.POST_DETAIL_URL)
        