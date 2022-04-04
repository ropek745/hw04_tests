from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовая пост',
        )


    def test_models_have_correct_object_names(self):
        '''Проверяем, что у моделей корректно работает __str__.'''
        # Проверяем правильное отображение значение поля __str__ в post
        post = PostModelTest.post
        self.assertEqual(str(post.text), post.text[:15])
        # Проверяем правильное отображение значения поля __str__ в group
        group = PostModelTest.group
        self.assertEqual(str(group.title), group.title)

