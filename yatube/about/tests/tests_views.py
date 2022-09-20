from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

PAGES = {
    reverse('about:author'): 'about/author.html',
    reverse('about:tech'): 'about/tech.html'
}


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_name(self):
        """URLs, генерируемые view классами author/, tech/, доступны."""
        for page in PAGES.keys():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_templates(self):
        """Проверка шаблонов для view классов author/, tech/."""
        for page, template in PAGES.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'{page} не возвращает шаблон {template}'
                )
