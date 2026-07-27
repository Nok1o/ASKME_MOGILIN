from django.test import TestCase
from django.urls import reverse


class PublicPagesTests(TestCase):
    def test_index_is_available(self):
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)

    def test_login_is_available(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)

    def test_missing_question_returns_404(self):
        response = self.client.get(reverse('question', args=[999]))

        self.assertEqual(response.status_code, 404)
