from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import WARNING
from .test_content import NotesUrls, NOTE_SLUG

User = get_user_model()


class TestLogic(NotesUrls):

    def test_anonymous_user_cant_create_note(self):
        '''Фиксируем кол-во заметок. Кол-во заметок не меняется.'''
        notes_count_start_test = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_start_test)

    def test_reader_can_create_note(self):
        '''Фиксируем кол-во заметок. Кол-во заметок увеличивается на 1.'''
        notes_count_start_test = Note.objects.count()
        self.author_client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_start_test + 1)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_note_cant_equal_slug(self):
        '''У разных заметок не может быть одинакого slug.'''
        notes_count_start_test = Note.objects.count()
        self.author_client.post(self.add_url, data=self.form_data)
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=NOTE_SLUG + WARNING,)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, notes_count_start_test + 1)

    def test_reader_can_create_notes_slug(self):
        '''Создаем заметку в чистой базе. Проверяем формирование slug.'''
        notes = Note.objects.all()
        notes.delete()
        notes_count_start_test = Note.objects.count()
        self.author_client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_start_test + 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, self.form_data['slug'])

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
        self.author_client.post(self.edit_url, data=self.form_data_new)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data_new['title'])
        self.assertEqual(self.note.text, self.form_data_new['text'])
        self.assertEqual(self.note.author, self.author)

    def test_reader_cant_edit_note(self):
        '''Заметку редактируем не автором. Заметка не изменилась.'''
        id = self.note.id
        old_note = Note.objects.get(id=id)
        self.reader_client.post(self.edit_url, data=self.form_data_new)
        new_note = Note.objects.get(id=id)
        self.assertEqual(new_note.title, old_note.title)
        self.assertEqual(new_note.text, old_note.text)
        self.assertEqual(new_note.author, old_note.author)
