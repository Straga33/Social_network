import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile


from posts.models import Post, Group, Comment, Follow


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug_2',
            description='Тестовое описание_2',
        )
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            post=cls.post,
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user_auth = User.objects.get(username='auth')
        self.authorized_client_auth = Client()
        self.authorized_client_auth.force_login(self.user_auth)

    def validating_post_fields(self, post):
        """Проверка полей поста"""
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)

    def test_group_post_page_show_post_in(self):
        """Проверка попадания поста в index, group_list, profile"""
        reverse_contains = (
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.user}),
        )
        for rev in reverse_contains:
            with self.subTest(rev=rev):
                response = self.authorized_client_auth.get(rev)
                self.assertTrue(
                    self.post in response.context['page_obj'].object_list
                )

    def test_group_post_page_show_post_not_in_group_2(self):
        """Проверка Group post page не попадает в другую группу"""
        response = self.authorized_client_auth.get(reverse(
            'posts:group_list', kwargs={'slug': self.group_2.slug}))
        self.assertFalse(
            self.post in response.context['page_obj'].object_list
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ):
                'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user}
            ):
                'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ):
                'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_auth.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client_auth.get(reverse('posts:index'))
        posts_context = response.context['page_obj'][0]
        self.validating_post_fields(posts_context)

    def test_group_posts_show_correct_context(self):
        """Шаблон  group_posts сформирован с правильным контекстом."""
        response = self.authorized_client_auth.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        posts_context = response.context['page_obj'][0]
        self.validating_post_fields(posts_context)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client_auth.get(
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        posts_context = response.context['page_obj'][0]
        self.validating_post_fields(posts_context)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client_auth.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        posts_context = response.context['post']
        self.validating_post_fields(posts_context)

    def test_post_detail_show_correct_comment(self):
        "В шаблоне post_detail сформирован с комментариями"
        response = self.authorized_client_auth.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertTrue(self.comment in response.context['comments_all'])

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client_auth.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client_auth.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(settings.NUB_OF_POSTS + 3):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый_пост_' + str(i),
                group=cls.group,
            )

    def setUp(self):
        self.user = User.objects.create(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test__page_contains_records(self):
        """Корректность работы Paginator."""
        reverse_contains = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        for rev in reverse_contains:
            with self.subTest(rev=rev):
                response = self.authorized_client.get(rev)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.NUB_OF_POSTS
                )
                response = self.authorized_client.get(rev + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class FollowTest(TestCase):
    def setUp(self):
        self.author = User.objects.create(username='auth')
        self.user = User.objects.create(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_not_follow = User.objects.create(username='User_not_follow')
        self.authorized_client_not_follow = Client()
        self.authorized_client_not_follow.force_login(self.user_not_follow)

    def test__user_follow_author(self):
        """Проверяем пользователь подписался на автора"""
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author})
        )
        self.assertRedirects(response, f'/profile/{self.author}/')
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )

    def test__user_unfollow_author(self):
        """Проверяем пользователь отписался от автора"""
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author})
        )
        self.assertRedirects(response, f'/profile/{self.author}/')
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )

    def test_new_post_see_only_follow(self):
        """Проверяем новая запись появляется у подписавшихся"""
        Follow.objects.create(
            user=self.user,
            author=self.author,
        )
        post = Post.objects.create(
            text='Пост для подписавшихся',
            author=self.author
        )
        response_auth = self.authorized_client.get(
            reverse('posts:follow_index')
        ).context['page_obj']
        self.assertIn(post, response_auth)

        response_not_auth = self.authorized_client_not_follow.get(
            reverse('posts:follow_index')
        ).context['page_obj']
        self.assertNotIn(post, response_not_auth)
