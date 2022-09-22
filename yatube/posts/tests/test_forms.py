import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings
from django.urls import reverse

from ..models import Comment, Post, User
from .user_creation import UserCreateTest


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostAndCommentCreateEditFormTests(UserCreateTest):

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Форма поста работает корректно."""
        posts_count = Post.objects.count()
        username = self.user.username
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post_data = {
            'text': 'Тестовый текст',
            'author': self.user,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=post_data,
            follow=True
        )
        where_to = reverse('posts:profile', kwargs={'username': f'{username}'})
        self.assertRedirects(response, where_to)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Тестовый текст',
            author=self.user,
            image='posts/small.gif'
        ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.redirect_chain[0][1], HTTPStatus.FOUND)

    def test_unauthorized_user_cannot_create_post(self):
        """Неавторизированному пользователю недоступно создание поста."""
        posts_count = Post.objects.count()
        username = self.guest_client
        post_data = {
            'text': 'Тестовый текст',
            'author': username
        }
        response = self.guest_client.post(
            reverse('posts:create_post'),
            data=post_data,
            follow=True
        )
        first_url = reverse('users:login')
        second_url = reverse('posts:create_post')
        where_to = f'{first_url}?next={second_url}'
        self.assertRedirects(response, where_to)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(
            text='Тестовый текст'
        ).exists()
        )
        self.assertEqual(response.redirect_chain[0][1], HTTPStatus.FOUND)

    def test_edit_post(self):
        """Форма редактирования поста работает корректно."""
        posts_count = Post.objects.count()
        post_id = self.post.id
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post_data = {
            'text': 'Кука-маркука, балям-барабука',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{post_id}'}),
            data=post_data,
            follow=True
        )
        post = Post.objects.filter(
            text='Кука-маркука, балям-барабука',
            author=self.user,
            image='posts/small.gif'
        )
        new_post_id = post[0].id
        where_to = reverse(
            'posts:post_detail', kwargs={'post_id': f'{post_id}'}
        )
        self.assertRedirects(response, where_to)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            text='Кука-маркука, балям-барабука',
            author=self.user,
            image='posts/small.gif'
        ).exists()
        )
        self.assertEqual(new_post_id, post_id)
        self.assertEqual(response.redirect_chain[0][1], HTTPStatus.FOUND)

    def test_comment_form(self):
        """Авторизированный пользователь может комментировать посты"""
        comments_count = Comment.objects.count()
        post = self.post
        post_id = post.id
        comment_data = {
            'text': 'Особенный тестовый текст',
            'author': self.user,
            'post': self.post
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': f'{post_id}'}),
            data=comment_data,
            follow=True
        )
        where_to = reverse(
            'posts:post_detail', kwargs={'post_id': f'{post_id}'}
        )
        response1 = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{post.id}'})
        )
        obj_in_response = response1.context['comments']
        comments = post.comments.all()
        index_of_latest_comment = len(obj_in_response) - 1
        new_comment = comments[index_of_latest_comment]
        text = new_comment.text
        self.assertIn(Comment.objects.filter(
            text='Особенный тестовый текст',
            author=self.user,
            post=self.post
        )[0], obj_in_response)
        self.assertEqual(text, 'Особенный тестовый текст')
        self.assertQuerysetEqual(
            obj_in_response,
            comments,
            transform=lambda x: x
        )
        self.assertRedirects(response, where_to)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(Comment.objects.filter(
            text='Особенный тестовый текст',
            author=self.user,
            post=self.post
        ).exists()
        )

    def test_comment_form_guest_client(self):
        """Неавторизированный пользователь не может комментировать посты"""
        post_id = self.post.id
        comments_count = Comment.objects.count()
        comment_data = {
            'text': 'Уникальный тестовый текст',
            'author': self.user,
            'post': self.post
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': f'{post_id}'}),
            data=comment_data,
            follow=True
        )
        first_url = reverse(
            'users:login'
        )
        next_url = reverse(
            'posts:add_comment', kwargs={'post_id': f'{post_id}'}
        )
        response1 = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{post_id}'})
        )
        obj_in_response = response1.context['comments']
        number_of_comments = len(obj_in_response)
        for i in range(1, number_of_comments):
            with self.subTest(i=i):
                text = obj_in_response[i].text
                self.assertNotEqual(
                    text, 'Уникальный тестовый текст'
                )
        self.assertEqual(comments_count, number_of_comments)
        self.assertRedirects(response, f'{first_url}?next={next_url}')
        self.assertFalse(Comment.objects.filter(
            text='Уникальный тестовый текст',
            author=self.user,
            post=self.post
        ).exists()
        )


class NotAuthorCannotEditTests(UserCreateTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='famed_author')
        cls.author = Client()
        cls.author.force_login(NotAuthorCannotEditTests.user)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Сверхуникальный текст',
        )

    def test_edit_post_not_author(self):
        """edit_post недоступно неавтору и неавторизированному пользователю."""
        posts_count = Post.objects.count()
        post_id = NotAuthorCannotEditTests.post.id
        post_data = {
            'text': 'Кука-маркука, балям-барабука',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{post_id}'}),
            data=post_data,
            follow=True
        )
        response1 = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{post_id}'}),
            data=post_data,
            follow=True
        )
        where_to = reverse(
            'posts:post_detail', kwargs={'post_id': f'{post_id}'}
        )
        first_url = reverse('users:login')
        second_url = reverse(
            'posts:post_edit', kwargs={'post_id': f'{post_id}'}
        )
        where_to1 = f'{first_url}?next={second_url}'
        responses = {
            response: where_to,
            response1: where_to1,
        }
        for response, where_to in responses.items():
            with self.subTest(response=response):
                self.assertRedirects(response, where_to)
                self.assertEqual(Post.objects.count(), posts_count)
                self.assertFalse(
                    Post.objects.filter(text='Тестовый текст').exists()
                )
                self.assertEqual(
                    response.redirect_chain[0][1], HTTPStatus.FOUND
                )
