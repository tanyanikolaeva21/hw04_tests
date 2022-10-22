from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post

User = get_user_model()


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Stesha')
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='test_slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='Stepashka')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post_id = self.post.id
        slug = self.group.slug
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_posts',
                kwargs={'slug': slug}),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.user}),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': post_id}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_uses_correct_template(self):
        """URL-адрес использует шаблон posts/create_post.html,
         чтобы отредактировать пост."""
        post_id = self.post.id
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_index_page_show_correct_context(self):
        """Шаблон posts/index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)

    def test_group_list_page_show_correct_context(self):
        """Шаблон posts/group_list.html сформирован с правильным контекстом."""
        slug = self.group.slug
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': slug})
        )
        self.assertEqual(response.context['group'].slug, self.group.slug)
