from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User

INDEX_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
LOGIN = reverse('users:login')

OK = HTTPStatus.OK
FAILED = HTTPStatus.NOT_FOUND
REDIRECT = HTTPStatus.FOUND

USERNAME = 'Roman'
USERNAME_1 = 'Pekarev'
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
POST_TEXT = 'I love django tests'

GROUP_LIST_URL = reverse('posts:posts_slug', kwargs={'slug': GROUP_SLUG})
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
NOT_FOUND_ULR = '/unexisting_page/'

CREATE_REDIRECT = f'{LOGIN}?next={CREATE_URL}'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.new_user = User.objects.create_user(username=USERNAME_1)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )
        cls.POST_DETAIL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.id}
        )
        cls.COMMENT = reverse(
            'posts:add_comment', kwargs={'post_id': cls.post.id}
        )
        cls.EDIT_REDIRECT = f'{LOGIN}?next={cls.POST_EDIT}'
        cls.COMMENT_REDIRECT = f'{LOGIN}?next={cls.POST_EDIT}comment/'

    def setUp(self):
        self.guest = Client()
        self.another = Client()
        self.author = Client()
        self.authorized_client_new = Client()
        self.author.force_login(self.user)
        self.authorized_client_new.force_login(self.new_user)

    def test_url_at_desired_location_for_any_user(self):
        """Проверка доступности адресов страниц для пользователя"""
        urls_names = [
            [INDEX_URL, self.guest, OK],
            [CREATE_URL, self.another, REDIRECT],
            [GROUP_LIST_URL, self.guest, OK],
            [PROFILE_URL, self.guest, OK],
            [self.POST_DETAIL, self.guest, OK],
            [self.POST_EDIT, self.another, REDIRECT],
            [CREATE_URL, self.author, OK],
            [self.POST_EDIT, self.author, OK],
            [self.POST_EDIT, self.another, REDIRECT],
            [NOT_FOUND_ULR, self.guest, FAILED],
            [self.COMMENT, self.guest, REDIRECT],
            [self.COMMENT, self.author, REDIRECT]
        ]
        for url, client, status in urls_names:
            with self.subTest(url=url, status=status):
                self.assertEqual(client.get(url).status_code, status)

    def url_redirect_anonymous_on_admin_login(self):
        """
        Страница в списке перенаправит анонимного
        пользователя на страницу логина.
        """
        urls_redirect_list = [
            [CREATE_URL, self.guest, CREATE_REDIRECT],
            [self.POST_EDIT, self.guest, self.EDIT_REDIRECT],
            [self.POST_EDIT, self.authorized_client_new, self.POST_DETAIL],
            [self.COMMENT, self.guest, self.COMMENT_REDIRECT]
        ]
        for url, client, redirect in urls_redirect_list:
            with self.subTest(url=url, redirect=redirect):
                self.assertRedirects(client.get(url, follow=True), redirect)

    def test_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_url_names = [
            [INDEX_URL, self.guest, 'posts/index.html'],
            [CREATE_URL, self.author, 'posts/create_post.html'],
            [GROUP_LIST_URL, self.author, 'posts/group_list.html'],
            [PROFILE_URL, self.guest, 'posts/profile.html'],
            [self.POST_DETAIL, self.guest, 'posts/post_detail.html'],
            [self.POST_EDIT, self.author, 'posts/create_post.html']
        ]
        for url, client, template in template_url_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(client.get(url), template)
