from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User

INDEX_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
LOGIN = reverse('users:login')

USERNAME = 'Roman'
USERNAME_1 = 'Pekarev'
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
POST_TEXT = 'I love django tests'
POST_ID = 6

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
            pk=POST_ID
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.id}
        )
        cls.EDIT_REDIRECT = f'{LOGIN}?next={cls.POST_EDIT_URL}'


    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_new = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_new.force_login(self.new_user)

    # Проверяем доступность страниц для неавторизированного пользователя

    def test_url_at_desired_location_for_any_user(self):
        """Проверка доступности адресов страниц для любого пользователя"""
        urls_names = {
            INDEX_URL: HTTPStatus.OK,
            GROUP_LIST_URL: HTTPStatus.OK,
            PROFILE_URL: HTTPStatus.OK,
            self.POST_DETAIL_URL: HTTPStatus.OK,
            NOT_FOUND_ULR: HTTPStatus.NOT_FOUND,
            self.POST_EDIT_URL: HTTPStatus.OK,
            CREATE_URL: HTTPStatus.OK,
        }
        for address, code_status in urls_names.items():
            with self.subTest(address=address):
                self.assertEqual(
                    self.authorized_client.get(address).status_code,
                    code_status
                )

    def url_redirect_anonymous_on_admin_login(self):
        """
        Страница в списке перенаправит анонимного
        пользователя на страницу логина.
        """
        urls_redirect_list = [
            [CREATE_URL, self.guest_client, CREATE_REDIRECT],
            [self.POST_EDIT_URL, self.guest_client, self.EDIT_REDIRECT]
            [self.POST_EDIT_URL, self.authorized_client_new, self.POST_DETAIL_URL]
        ]
        for url, client, redirect in urls_redirect_list:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url, follow=True), redirect)

    # Проверка вызываемых шаблонов

    def test_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_url_names = [
            [INDEX_URL, self.guest_client, 'posts/index.html'],
            [CREATE_URL, self.authorized_client, 'posts/create_post.html'],
            [GROUP_LIST_URL, self.authorized_client, 'posts/group_list.html'],
            [PROFILE_URL, self.guest_client, 'posts/profile.html'],
            [self.POST_DETAIL_URL, self.guest_client, 'posts/post_detail.html'],
            [self.POST_EDIT_URL, self.authorized_client, 'posts/create_post.html']
        ]
        for url, client, template in template_url_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(client.get(url), template)