from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Pet

class RenamePetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='p')
        # Pet auto-created on signup in app flow, but ensure exists for tests
        Pet.objects.get_or_create(user=self.user)

    def test_requires_authentication(self):
        resp = self.client.post(reverse('rename_pet'), {'name': 'Buddy'})
        self.assertEqual(resp.status_code, 302)  # redirect to login

    def test_rename_success(self):
        self.client.login(username='u', password='p')
        resp = self.client.post(reverse('rename_pet'), {'name': 'Buddy'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data['pet']['name'], 'Buddy')
        self.user.refresh_from_db()
        self.assertEqual(self.user.pet.name, 'Buddy')

    def test_rename_invalid_empty(self):
        self.client.login(username='u', password='p')
        resp = self.client.post(reverse('rename_pet'), {'name': '   '})
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data.get('success'))
        self.assertIn('name', data.get('errors', {}))

    def test_rename_too_long(self):
        self.client.login(username='u', password='p')
        long_name = 'x' * 31
        resp = self.client.post(reverse('rename_pet'), {'name': long_name})
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data.get('success'))
        self.assertIn('name', data.get('errors', {}))
