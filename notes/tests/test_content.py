from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from django.contrib.auth import get_user_model
from notes.forms import NoteForm


User = get_user_model()

NOTE_COUNT_FOR_TEST = 10


class TestListNotesPageOneUser(TestCase):
    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.first_user = User.objects.create(username='Лев Толстой')
        cls.second_user = User.objects.create(username='Анжей Ясинский')
        notes_first_user = [
            Note(
                title=f'Заметка {cls.first_user} № {index}',
                text=f'Текст заметки {index}',
                author=cls.first_user,
                slug=index,
            )
            for index in range(NOTE_COUNT_FOR_TEST)
        ]
        Note.objects.bulk_create(notes_first_user)
        # Создаем тестовую заметку
        cls.note = Note.objects.create(
            title='Тест передачи отдельной заметки',
            text='Текст',
            author=cls.first_user,)
        notes_second_user = [
            Note(
                title=f'Заметка {cls.second_user} № {index}',
                text=f'Текст заметки {index}',
                author=cls.second_user,
                slug=index+NOTE_COUNT_FOR_TEST,
            )
            for index in range(NOTE_COUNT_FOR_TEST)
        ]
        Note.objects.bulk_create(notes_second_user)

    def test_note_drive(self):
        self.client.force_login(self.first_user)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        all_title = [note.title for note in object_list]
        self.assertIn('Тест передачи отдельной заметки', all_title)

    def test_notes_first_out_second_users(self):
        self.client.force_login(self.first_user)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        all_title_first_user = [note.title for note in object_list]
        self.client.force_login(self.second_user)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        all_title_second_user = [note.title for note in object_list]
        for title in all_title_first_user:
            self.assertNotIn(title, all_title_second_user)

    def test_pages_contains_form(self):
        self.client.force_login(self.first_user)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)
        
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
