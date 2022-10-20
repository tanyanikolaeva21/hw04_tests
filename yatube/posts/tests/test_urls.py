from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name',
                                            email='test@ya.ru',
                                            password='pass',
                                            text='Тестовая запись',
                                    )
        )
        cls.group = Group.objects.create(
            title=('Название тестовой группы'),
            slug='test_slug'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Stesha')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_and_group(self):
        """страницы группы и главная доступны всем"""
        url_names = (
            '/',
            '/group/test_slug/',
        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_for_authorized(self):
        """Страница /create доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_url(self):
        """без авторизации приватные URL недоступны"""
        url_names = (
            '/create/',
            '/admin/',
        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_redirect_anonymous_on_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/signup/'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            'group_list.html': '/group/test_slug/',
            'create_post.html': '/create/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        response = self.guest_client.get('/unexisting/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
