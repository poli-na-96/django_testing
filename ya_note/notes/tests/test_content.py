from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Пользователь')
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(
            title='Заметка',
            author=cls.author,
            text='Текст заметки'
        )

    def test_note_in_list_for_author(self):
        url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        url = reverse('notes:list')
        self.client.force_login(self.reader)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_page_add_note_contains_form(self):
        url = reverse('notes:add')
        self.client.force_login(self.reader)
        response = self.client.get(url)
        self.assertIn('form', response.context)

    def test_page_adit_note_contains_form(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.get(url)
        self.assertIn('form', response.context)
