from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post
from .user_creation import UserCreateTest

User = get_user_model()


class StaticURLTests(TestCase):
    """Первое, так называемое "дымовое", тестирование."""
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

# Несуществующая страница выдает ошибку 404
# и кастомный шаблон - в приложении core


class PostURLTests(UserCreateTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='famed_author')
        cls.author = Client()
        cls.author.force_login(PostURLTests.user)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Сверхуникальный текст',
        )

    def test_urls_exists_at_desired_location(self):
        """Общедоступные страницы доступны неавторизированному пользователю."""
        post = self.post
        group = self.group
        post_id = post.id
        user = self.user
        PAGES = (
            '/',
            f'/group/{group.slug}/',
            f'/profile/{user.username}/',
            f'/posts/{post_id}/'
        )
        for page in PAGES:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Адрес {page} не доступен'
                )

    def test_create_url_exists_at_desired_location(self):
        """Страница create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Страница create/ не доступна авторизированному пользователю'
        )

    def test_create_url_redirect_anonymous_on_login(self):
        """Страница create/ перенаправляет неавторизированного пользователя."""
        msg = (
            'Страница create/ Не перенаправила '
            'неавторизированного пользователя'
        )
        first_url = reverse('users:login')
        next_url = reverse('posts:create_post')
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response,
            f'{first_url}?next={next_url}',
            msg_prefix=msg
        )

    def test_edit_url_exists_at_desired_location(self):
        """Страница edit доступна автору поста."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Страница /edit/ не доступна автору поста'
        )

    def test_edit_url_redirects(self):
        """Страница edit не доступна Не-автору поста."""
        post = PostURLTests.post
        response = self.authorized_client.get(
            f'/posts/{post.id}/edit/',
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': f'{post.id}'}),
            msg_prefix='Страница edit/ доступна не автору поста'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post = self.post
        group = self.group
        post_id = post.id
        user = self.user
        PAGES_TEMPLATES_NAMES = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{user.username}/': 'posts/profile.html',
            f'/posts/{post_id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{post_id}/edit/': 'posts/create_post.html'
        }
        for page, template in PAGES_TEMPLATES_NAMES.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Нет шаблона {template} на странице {page}'
                )
