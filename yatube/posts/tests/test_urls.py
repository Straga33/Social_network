from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus


from posts.models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_auth = User.objects.get(username='auth')
        self.authorized_client_auth = Client()
        self.authorized_client_auth.force_login(self.user_auth)

    def test_home_posts_edit_auth(self):
        response = self.authorized_client_auth.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_home_posts_create(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url(self):
        field_verboses = {
            '/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.guest_client.get(field).status_code,
                    expected_value,
                )

    def test_posts_url_Redirects(self):
        field_verboses = {
            f'/posts/{self.post.id}/edit/':
            f'/auth/login/?next=/posts/{self.post.id}/edit/',
            '/create/': '/auth/login/?next=/create/',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertRedirects(
                    self.guest_client.get(field, follow=True),
                    expected_value
                )

    def test_post_url_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_auth.get(address)
                self.assertTemplateUsed(response, template)

class Page404Tests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_page_not_found(self):
        """Проверяем, что страница 404 отдает кастомный шаблон"""
        response = self.guest_client.get('page_not_found')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
