from ..models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='stesha')
        cls.group = Group.objects.create(
            title='название',
            slug='slug',
            description='описание'
        )

    def setUp(self):
        self.user = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_post_create_by_login_user(self):
        """Проверка создания поста"""
        count = Post.objects.count()
        form_data = {
            'text': 'тестирование',
            'group': self.group.id,
        }
        url = reverse('posts:post_create')
        response = self.author_client.post(url, data=form_data, follow=True)
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.author.username}))
        self.assertEqual(Post.objects.count(), count + 1)

    def test_post_edit(self):
        post = Post.objects.create(
            text='тестирование',
            author=self.author,
            group=self.group,
            id=1,
        )

        form_data = {
            'text': 'тестирование',
            'group': self.group.id,
        }
        url = reverse('posts:post_detail', kwargs={'post_id': post.id})
        response = self.author_client.post(url, data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])