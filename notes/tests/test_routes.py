from http import HTTPStatus

from django.contrib.auth import get_user_model

from .confunittest import NotesUrls


User = get_user_model()


class TestRoutes(NotesUrls):

    def test_pages_availability(self):
        urls = (
            self.home_url,
            self.login_url,
            self.logout_url,
            self.signup_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_have_access(self):
        urls = (
            self.list_url,
            self.add_url,
            self.success_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, self.author_client, HTTPStatus.OK),
            (self.reader, self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, user_client, status in users_statuses:
            for url in (self.edit_url, self.detail_url, self.delete_url):
                with self.subTest(user=user, url=url):
                    response = user_client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        for url in (self.edit_url, self.detail_url, self.delete_url):
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
