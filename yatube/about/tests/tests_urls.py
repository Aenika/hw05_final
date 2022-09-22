from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


URLS = (
    reverse('about:author'),
    reverse('about:tech'),
)


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exist_at_desired_location(self):
        """Проверка доступности адресoв author/ и tech/."""
        for url in URLS:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Адрес {url} не доступен.'
                )
