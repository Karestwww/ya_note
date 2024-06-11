from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from .confunittest import NotesUrls

User = get_user_model()


class TestListNotesPageOneUser(NotesUrls):

    def test_note_drive(self):
        """Проверка наличия одиночной заметки автора в его списке заметок."""
        response = self.author_client.get(self.list_url)
        authors_notes = response.context['object_list']
        self.assertIn(self.note, authors_notes)

    def test_notes_author_out_notes_reader(self):
        """Проверка в списке заметок автора нет заметок где автор читатель."""
        response = self.author_client.get(self.list_url)
        authors_notes = response.context['object_list']
        authors_in_authors_notes = [note.author for note in authors_notes]
        self.assertNotIn(self.reader, authors_in_authors_notes)
        self.assertIn(self.author, authors_in_authors_notes)

    def test_pages_contains_form(self):
        urls = (self.add_url, self.edit_url,)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
