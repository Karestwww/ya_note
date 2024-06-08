from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
from pytils.translit import slugify # type: ignore

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_SLUG = 'Slug'

    @classmethod
    def setUpTestData(cls):
        # Адрес страницы с заметкой.
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Анжей Ясинский')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'title': 'Название заметки',
                         'text': 'Текст заметки',
                         'slug': cls.NOTE_SLUG}

    def test_anonymous_user_cant_create_note(self):
        # Фиксируем кол-во заметок (не зависить от входных данных)
        notes_count_start_test = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        # Проверяем, что кол-во заметок не увеличилось
        self.assertEqual(notes_count, notes_count_start_test)

    def test_user_can_create_note(self):
        # Фиксируем кол-во заметок (не зависить от входных данных)
        notes_count_start_test = Note.objects.count()
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        # Проверяем, что кол-во заметок увеличилось на 1
        self.assertEqual(notes_count, notes_count_start_test+1)

    def test_note_cant_equal_slug(self):
        self.auth_client.post(self.url, data=self.form_data)
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.NOTE_SLUG+WARNING,)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 1)


class TestCreationStandartSlug(TestCase):
    NOTE_TITLE = 'Тестовая заметка'

    @classmethod
    def setUpTestData(cls):
        # Адрес страницы с заметкой.
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Анжей Ясинский')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'title': cls.NOTE_TITLE, 'text': 'Текст заметки'}

    def test_user_can_create_notes_slug(self):
        # Фиксируем кол-во заметок (не зависить от входных данных)
        notes_count_start_test = Note.objects.count()
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        # Проверяем, что кол-во заметок увеличилось на 1
        self.assertEqual(notes_count, notes_count_start_test+1)
        # Получаем созданную заметку из базы
        new_note = Note.objects.get()
        # Создаем слаг согласно логике модели
        expected_slug = slugify(self.NOTE_TITLE)
        # Проверяем, что slug сформировался ожидаемым
        self.assertEqual(new_note.slug, expected_slug)

class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Тестовая заметка'
    NOTE_TEXT = 'Текст тестовой заметки'
    NEW_TITLE = 'Измененная заметка'
    NEW_NOTE_TEXT = 'Текст изменненой заметки'


    @classmethod
    def setUpTestData(cls):
        # Создаём пользователей - автора заметок и пользователя
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Анжей Ясинский')
        # Создаём клиент для автора заметок и пользователя
        cls.author_client = Client()
        cls.reader_client = Client()
        # "Логиним" автора в клиенте.
        cls.author_client.force_login(cls.author)
        # Создаем тестовую заметку
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,)
        # Определяем URL для редактирования заметки.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,)) 
        # Определяем URL для удаления заметки.
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))  
        # Формируем данные для POST-запроса для обновления заметки.
        cls.form_data = {'title': cls.NEW_TITLE, 'text': cls.NEW_NOTE_TEXT}

    def test_author_can_delete_note(self):
        # Фиксируем кол-во заметок (не зависить от входных данных)
        notes_count_start_test = Note.objects.count()
        # От имени автора отправляем DELETE-запрос на удаление.
        self.author_client.delete(self.delete_url)
        # Считаем количество заметок в системе.
        notes_count = Note.objects.count()
        # Проверяем, что кол-во заметок уменьшилось на 1
        self.assertEqual(notes_count, notes_count_start_test-1)

    def test_reader_cant_delete_note(self):
        # Фиксируем кол-во заметок (не зависить от входных данных)
        notes_count_start_test = Note.objects.count()
        # От имени пользователя отправляем DELETE-запрос на удаление.
        self.reader_client.delete(self.delete_url)
        # Считаем количество заметок в системе.
        notes_count = Note.objects.count()
        # Проверяем, что кол-во заметок не изменилось
        self.assertEqual(notes_count, notes_count_start_test)

    def test_author_can_edit_note(self):
        # Выполняем запрос на редактирование от имени автора заметки.
        self.author_client.post(self.edit_url, data=self.form_data)
        # Обновляем объект заметки.
        self.note.refresh_from_db()
        # Проверяем, что заметка обновилась.
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_reader_cant_edit_note(self):
        # Выполняем запрос на редактирование от имени пользователя заметки.
        self.reader_client.post(self.edit_url, data=self.form_data)
        # Обновляем объект заметки.
        self.note.refresh_from_db()
        # Проверяем, что заметка не изменилась.
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
