from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_SLUG = 'Test_slug'
    NOTE_TITLE = 'Тестовая заметка'

    @classmethod
    def setUpTestData(cls):
        '''Определяем адрес страницы с заметкой, пользователя, заметку.'''
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Анжей Ясинский')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'title': cls.NOTE_TITLE,
                         'text': 'Текст заметки',
                         'slug': cls.NOTE_SLUG}

    def test_anonymous_user_cant_create_note(self):
        '''Фиксируем кол-во заметок. Кол-во заметок не меняется.'''
        notes_count_start_test = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_start_test)

    def test_user_can_create_note(self):
        '''Фиксируем кол-во заметок. Кол-во заметок увеличивается на 1.'''
        notes_count_start_test = Note.objects.count()
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_start_test + 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_note_cant_equal_slug(self):
        notes_count_start_test = Note.objects.count()
        self.auth_client.post(self.url, data=self.form_data)
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.NOTE_SLUG + WARNING,)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, notes_count_start_test + 1)

    def test_user_can_create_notes_slug(self):
        '''Создаем заметку в чистой базе. Проверяем формирование slug.'''
        notes = Note.objects.all()
        notes.delete()
        notes_count_start_test = Note.objects.count()
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_start_test + 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, self.form_data['slug'])


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Тестовая заметка'
    NOTE_TEXT = 'Текст тестовой заметки'
    NEW_TITLE = 'Измененная заметка'
    NEW_NOTE_TEXT = 'Текст изменненой заметки'

    @classmethod
    def setUpTestData(cls):
        '''Создаём заметку ее автора и пользоватлея, urls, POST-запрос.'''
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Анжей Ясинский')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'title': cls.NEW_TITLE, 'text': cls.NEW_NOTE_TEXT}

    def test_author_can_delete_note(self):
        '''Фиксируем кол-во заметок. Кол-во заметок уменьшилось на 1.'''
        notes_count_start_test = Note.objects.count()
        self.author_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_start_test - 1)

    def test_reader_cant_delete_note(self):
        '''Фиксируем кол-во заметок. Кол-во заметок не изменилось.'''
        notes_count_start_test = Note.objects.count()
        self.reader_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_start_test)

    def test_author_can_edit_note(self):
        '''Заметку редактируем автором. Фиксация ее изменения.'''
        self.author_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.author, self.author)

    def test_reader_cant_edit_note(self):
        '''Заметку редактируем не автором. Заметка не изменилась.'''
        id=self.note.id
        self.reader_client.post(self.edit_url, data=self.form_data)
        fresh_note = Note.objects.get(id=id)
        self.assertEqual(fresh_note.title, self.NOTE_TITLE)
        self.assertEqual(fresh_note.text, self.NOTE_TEXT)
        self.assertEqual(fresh_note.author, self.author)
