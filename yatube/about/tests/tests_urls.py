from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()

URLS = (
    '/about/author/',
    '/about/tech/'
)


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='minion')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_urls_exist_at_desired_location(self):
        """Проверка доступности адресoв author/ и tech/."""
        guest = self.guest_client
        authorized = self.authorized_client
        CLIENTS = (guest, authorized)
        for client in CLIENTS:
            for url in URLS:
                with self.subTest(url=url):
                    response = client.get(url)
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.OK,
                        f'Адрес {url} не доступен пользователю {client}'
                    )
