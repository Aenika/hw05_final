"""Создает данные для тестирований."""

import shutil
import tempfile

import django.test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@django.test.override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserCreateTest(django.test.TestCase):

    def setUp(self):
        cache.clear()
        self.guest_client = django.test.Client()
        self.user = User.objects.create_user(username='minion')
        self.authorized_client = django.test.Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Многословное художественное описание группы')
        small_gif1 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded1 = SimpleUploadedFile(
            name='small1.gif',
            content=small_gif1,
            content_type='image/gif'
        )
        self.post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Блаблабла' * 100,
            image=uploaded1)
        self.pages = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}),
            reverse(
                'posts:profile', kwargs={'username': f'{self.user.username}'}
            )
        )
        self.comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            text='Лалала' * 5
        )

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
