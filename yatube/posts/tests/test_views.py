from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.paginator import Page
from django.db.models.fields.files import ImageFieldFile
from django.db.models.query import QuerySet
from django.test import Client
from django.urls import reverse

from ..forms import CommentForm
from ..models import Follow, Group, Post
from .user_creation import UserCreateTest

User = get_user_model()

POSTS_PER_PAGE = settings.POSTS_PER_PAGE
POSTS_FOR_PAGINATOR_TESTING = 13


class PagesTemplatesTests(UserCreateTest):

    def test_pages_use_correct_templates(self):
        """view-классы используют соответствующие шаблоны."""
        post = self.post
        group = self.group
        post_id = post.id
        user = self.user
        pages_templates_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:create_post'): 'posts/create_post.html',
            reverse('posts:group_list', kwargs={'slug': f'{group.slug}'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': f'{user.username}'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': f'{post_id}'}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': f'{post_id}'}):
                'posts/create_post.html',
        }

        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                msg = f'по адресу {reverse_name} нет шаблона {template}'
                self.assertTemplateUsed(
                    response,
                    template,
                    msg_prefix=msg
                )


class TestingPaginator(UserCreateTest):

    def setUp(self):
        super().setUp()
        self.posts_for_test = []
        for i in range(1, POSTS_FOR_PAGINATOR_TESTING):
            self.posts_for_test.append(Post(
                author=self.user,
                text=f'Test{i}',
                group=self.group))
        Post.objects.bulk_create(self.posts_for_test)

    def test_first_page_contain_expected_number_records_and_class_page(self):
        """Проверка паджинатора и использования класса Page в контексте."""
        number_of_posts = len(Post.objects.all())
        # так как в родительском классе создавался тестовый пост,
        # число постов не совпадает с len(self.posts_for_test)
        posts_on_second_page = number_of_posts - POSTS_PER_PAGE
        for page in self.pages:
            with self.subTest(page=page):
                response1 = self.client.get(page)
                response2 = self.client.get(page + '?page=2')
                context = response1.context['page_obj']
                self.assertEqual(
                    len(response1.context['page_obj']),
                    POSTS_PER_PAGE,
                    f'На странице {page} должно быть {POSTS_PER_PAGE} постов'
                )
                self.assertEqual(
                    len(response2.context['page_obj']),
                    posts_on_second_page,
                    f'На второй странице {page} '
                    f'должно быть {posts_on_second_page} постов'
                )
                self.assertIsInstance(
                    context,
                    Page,
                    f'На станице {page} нет класса Page в контексте'
                )


class PostsPagesTests(UserCreateTest):

    def test_create_and_edit_uses_form_in_context(self):
        """Шаблоны create и post_edit используют форму корректно."""
        post = self.post
        ADDRESSES = (
            reverse('posts:create_post'),
            reverse('posts:post_edit', kwargs={'post_id': f'{post.id}'}),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for address in ADDRESSES:
            response = self.authorized_client.get(address)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_post_detail_and_edit_use_correct_context(self):
        """Шаблоны post_detail и edit/ используют ожидаемый контекст."""
        group = self.group
        post = self.post
        author = post.author
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{post.id}'})
        )
        response2 = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{post.id}'})
        )
        OBJS_IN_RESPONSES = (
            response.context['post'],
            response2.context['form'].instance
        )
        for obj_in_response in OBJS_IN_RESPONSES:
            post_text = obj_in_response.text
            post_group = obj_in_response.group
            post_author = obj_in_response.author
            post_image = obj_in_response.image
            self.assertEqual(obj_in_response, post)
            self.assertEqual(post_text, 'Блаблабла' * 100)
            self.assertEqual(post_group, group)
            self.assertEqual(post_author, author)
            self.assertEqual(post_image, 'posts/small1.gif')
            self.assertIsInstance(post_image, ImageFieldFile)

    def test_post_detail_uses_comments_in_context(self):
        """Шаблон post_detail использует комментарии в контексте."""
        post = self.post
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{post.id}'})
        )
        comments_in_response = response.context['comments']
        form_in_response = response.context['form']
        post_text = comments_in_response[0].text
        self.assertIsInstance(comments_in_response, QuerySet)
        self.assertEqual(post_text, 'Лалала' * 5)
        self.assertIsInstance(form_in_response, CommentForm)

    # То, что в контексте есть Page
    # протестировано вместе с паджинатором

    def test_group_list_uses_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group = self.group
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': f'{group.slug}'})
        )
        context = response.context['group']
        self.assertIsInstance(context, Group)

    def test_profile_uses_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        user = self.user
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': f'{user.username}'}
        ))
        context = response.context['author']
        context2 = response.context['posts_by_author']
        posts_count = user.posts.count()
        self.assertIsInstance(context, User)
        self.assertIsInstance(context2, QuerySet)
        self.assertEqual(len(context2), posts_count)

    def test_pages_show_correct_context_for_post(self):
        """Шаблоны сформированы с правильным контекстом(содержание Post)."""
        group = self.group
        pages = self.pages
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                first_object = response.context['page_obj'][0]
                post_text_0 = first_object.text
                post_group_0 = first_object.group
                post_image_0 = first_object.image
                self.assertEqual(post_text_0, 'Блаблабла' * 100)
                self.assertEqual(post_group_0, group)
                self.assertEqual(post_image_0, 'posts/small1.gif')
                self.assertIsInstance(post_image_0, ImageFieldFile)

    def test_edit_post_uses_is_edit(self):
        """Шаблон post_edit использует булеву переменную is_edit корректно."""
        post = self.post
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{post.id}'})
        )
        context = response.context['is_edit']
        self.assertIsInstance(context, bool)
        self.assertEqual(context, True)


class PostsOnCreationTest(UserCreateTest):

    def setUp(self):
        super().setUp()
        self.group1 = Group.objects.create(
            title='Еще тестовая группа',
            slug='testslug1'
        )

    def test_post_is_on_expected_pages(self):
        """Проверяем, что пост есть на нужных страницах."""

        post = self.post
        pages = self.pages
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                context = response.context['page_obj']
                self.assertIn(post, context)

    def test_not_in_unrelated_group(self):
        """Проверяем, что поста нет в группе, к которой он не относится."""
        # Пост относится к группе self.group
        post = self.post
        group = self.group1
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': f'{group.slug}'}
        ))
        context = response.context['page_obj']
        self.assertNotIn(post, context)


class CacheTest(UserCreateTest):

    def test_cache(self):
        """Главная страница работает с кэшем корректно."""
        author = self.user
        response = self.guest_client.get(
            reverse('posts:index')
        )
        Post.objects.filter(
            text='Блаблабла' * 100,
            author=author,
        ).delete()
        response1 = self.guest_client.get(
            reverse('posts:index')
        )
        self.assertEqual(response.content, response1.content)
        cache.clear()
        response_new = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_new.content)


class FollowSystemTest(UserCreateTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='famed_author')
        cls.author = Client()
        cls.author.force_login(FollowSystemTest.user)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Сверхуникальный текст',
        )

    def setUp(self):
        super().setUp()
        self.user1 = User.objects.create_user(username='minion1')
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

    def test_follow(self):
        """Подписки работают корректно."""
        following = FollowSystemTest.user
        follower = self.user
        Follow.objects.create(user=follower, author=following)
        post_by_autor = Post.objects.filter(author=following)[0]
        response = self.authorized_client.get(reverse('posts:follow_index'))
        context = response.context['page_obj']
        self.assertIn(post_by_autor, context)
        response1 = self.authorized_client1.get(reverse('posts:follow_index'))
        context1 = response1.context['page_obj']
        self.assertNotIn(post_by_autor, context1)
        Follow.objects.filter(user=follower, author=following).delete()
        response2 = self.authorized_client.get(reverse('posts:follow_index'))
        context2 = response2.context['page_obj']
        self.assertNotIn(post_by_autor, context2)
