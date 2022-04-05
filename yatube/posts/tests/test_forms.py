import shutil
import tempfile
from django.core.cache import cache

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings


from posts.models import Group, Post


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_create_post(self):
        """Валидная форма создает запись post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст формы',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Тестовый текст формы',
                group=self.group.id,
                image='posts/small.gif',
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись post."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный Тестовый текст формы',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Измененный Тестовый текст формы',
                group=self.group.id,
            ).exists()
        )

    def test_cache(self):
        """Кэш хранит контент сраницы до очищения."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост кэш',
            group=self.group,
        )
        response = self.authorized_client.get(reverse('posts:index')).content
        Post.objects.last().delete()
        response_after = self.authorized_client.get(
                            reverse('posts:index')).content
        self.assertEqual(response, response_after)
        cache.clear()
        response_after = self.authorized_client.get(
                            reverse('posts:index')).content
        self.assertNotEqual(response, response_after)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.user_not_authorized = User.objects.create(username='HasNoName')
        self.user_authorized = User.objects.create(username='Sold')
        self.not_authorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_authorized)

    def test_comment_add_authorized_user(self):
        "Провека, комментировать может только авторизованный пользователь"
        form_data_auth = {
            'post': self.post,
            'author': self.user_authorized,
            'text': 'Пользователь авторизован',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data_auth,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        form_data_not_auth = {
            'post': self.post,
            'author': self.user_not_authorized,
            'text': 'Пользователь не авторизован',
        }
        response = self.not_authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data_not_auth,
            follow=True
        )
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next=/posts/1/comment/"
        )
