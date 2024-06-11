from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

NOTE_COUNT_FOR_TEST = 10
NOTE_SLUG = 'Test_slug'
NOTE_TITLE = 'Тестовая заметка'
NOTE_TEXT = 'Текст тестовой заметки'
NEW_TITLE = 'Измененная заметка'
NEW_NOTE_TEXT = 'Текст изменненой заметки'


class NotesUrls(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {'title': NOTE_TITLE,
                         'text': NOTE_TEXT,
                         'slug': NOTE_SLUG}
        cls.form_data_new = {'title': NEW_TITLE,
                             'text': NEW_NOTE_TEXT}
        notes_author = [
            Note(
                title=f'Заметка {cls.author} № {index}',
                text=f'Текст заметки {index}',
                author=cls.author,
                slug=index,
            )
            for index in range(NOTE_COUNT_FOR_TEST)
        ]
        Note.objects.bulk_create(notes_author)
        # Создаем одиночную заметку
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            author=cls.author,)
        notes_reader = [
            Note(
                title=f'Заметка {cls.reader} № {index}',
                text=f'Текст заметки {index}',
                author=cls.reader,
                slug=index + NOTE_COUNT_FOR_TEST,
            )
            for index in range(NOTE_COUNT_FOR_TEST)
        ]
        Note.objects.bulk_create(notes_reader)
        cls.add_url = reverse('notes:add')
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.home_url = reverse('notes:home')
        cls.list_url = reverse('notes:list')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.success_url = reverse('notes:success')