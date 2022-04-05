from django.test import TestCase
from django.contrib.auth import get_user_model


from posts.models import Post, Group


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def setUp(self):
        self.post = PostModelTest.post

    def test_models_post_have_correct_object_names(self):
        """Проверяем, модель поста корректно работает __str__."""
        self.assertEqual(self.post.text[:15], str(self.post))

    def test_models_post_have_verbose_name(self):
        """Проверяем, модель поста корректно verbose_name."""
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_models_post_have_help_text(self):
        """Проверяем, модель поста корректно help_text."""
        field_verboses = {
            'text': 'Текст нового поста',
            'author': 'Автор поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    expected_value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def setUp(self):
        self.group = GroupModelTest.group

    def test_models_group_have_correct_object_names(self):
        """Проверяем, модель группы корректно работает __str__."""
        self.assertEqual(self.group.title, str(self.group))

    def test_models_group_have_verbose_name(self):
        """Проверяем, модель группы корректно verbose_name."""
        field_verboses = {
            'title': 'Заголовок группы',
            'slug': 'Идентификатор',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_models_group_have_help_text(self):
        """Проверяем, модель группы корректно help_text."""
        field_verboses = {
            'title': 'Заголовок новой группы',
            'slug': 'Идентификатор группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).help_text,
                    expected_value
                )
