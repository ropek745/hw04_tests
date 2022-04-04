from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group
from posts.forms import PostForm
User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём запись в базе данных для проверки существующего slug
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
        cls.form = PostForm()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.authorized_client = Client()
        # Авторизуем клиента
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создаёт запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'text': 'Текстовая пост',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, 
            reverse('posts:profile', args=[self.user])
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись
        self.assertTrue(Post.objects.filter(
            text='Текстовая пост',
            group=self.group).exists())

    def test_post_edit(self):
        # Создаём форму
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.pk]),
            data=form_data,
            follow=True
        )
        post = response.context.get('post')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.post.author)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=[self.post.id])
        )
        self.assertTrue(Post.objects.filter(
            text='Отредактированный текст поста',
            group=self.group.id).exists()
        )
