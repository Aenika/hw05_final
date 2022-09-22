from django.test import TestCase

from core.constants import SYMBOLS_FOR_PREVIEW
from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='minion')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Многословное художественное описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Блаблабла' * 100,
        )

    def test_verbose_names(self):
        """verbose_name в полях group, post совпадает с ожидаемым."""
        group = PostModelTest.group
        post = PostModelTest.post
        GROUP_FIELD_VERBOSES = {
            'title': 'Название',
            'slug': 'Слаг',
            'description': 'Описание',
        }

        POST_FIELD_VERBOSES = {
            'text': 'Текст поста',
            'group': 'Группа',
            'author': 'Автор',
            'image': 'Картинка'
        }

        FIELD_VERBOSES = {
            group: GROUP_FIELD_VERBOSES,
            post: POST_FIELD_VERBOSES
        }

        for model, field_verboses in FIELD_VERBOSES.items():
            for field, expected_value in field_verboses.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).verbose_name,
                        expected_value,
                        f'verbose_name {field} не совпадает с {expected_value}'
                    )

    def test_post_help_text(self):
        """help_text в полях group совпадает с ожидаемым."""
        post = PostModelTest.post
        field_helpers = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Загрузите картинку'
        }
        for field, expected_value in field_helpers.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value,
                    f'help_text поля {field} не совпадает с {expected_value}'
                )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        group_title = group.title
        post = PostModelTest.post
        post_title = post.text[:SYMBOLS_FOR_PREVIEW]
        EXPECTED_VALUE = {
            group: group_title,
            post: post_title
        }
        for model, expected_value in EXPECTED_VALUE.items():
            with self.subTest(model=model):
                self.assertEqual(
                    expected_value,
                    str(model),
                    f'str модели {model} не совпадает с {expected_value}'
                )
