from http import HTTPStatus

from django.test import TestCase


class Test404(TestCase):
    def test_error_page(self):
        """Страница 404 возвращает ожидаемый шаблон и выдает ошибку 404"""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")
