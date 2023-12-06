from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Пользователь')
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заметка',
            author=cls.author,
            text='Текст заметки'
        )

    def test_pages_availability_for_anonymous_user(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for url in urls:
            with self.subTest(url=url):
                url = reverse(url)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            'notes:list',
            'notes:add',
            'notes:success'
        )
        for url in urls:
            with self.subTest():
                url = reverse(url)
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in ('notes:detail',
                         'notes:edit',
                         'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        pages = (
            ('notes:detail'),
            ('notes:edit'),
            ('notes:delete'),
        )
        for name in pages:
            login_url = reverse('users:login')
            url = reverse(name, args=(self.note.slug,))
            expected_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, expected_url)

    def test_redirects(self):
        pages = (
            ('notes:add'),
            ('notes:success'),
            ('notes:list'),
        )
        for name in pages:
            login_url = reverse('users:login')
            url = reverse(name)
            expected_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, expected_url)
