from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .test_content import NotesUrls


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
            self.client.force_login(user)
            for url in (self.edit_url, self.detail_url, self.delete_url):
                with self.subTest(user=user, url=url):
                    response = user_client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for url in (self.edit_url, self.detail_url, self.delete_url):
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
