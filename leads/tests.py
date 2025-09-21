from django.test import TestCase
from django.urls import reverse

from .models import Lead


class LeadModelTest(TestCase):
    def test_create_lead(self):
        lead = Lead.objects.create(name='Teste', email='teste@example.com')
        self.assertEqual(str(lead), 'Teste (Pessoa Física)')


class LeadDashboardViewTest(TestCase):
    def test_dashboard_view_returns_200(self):
        response = self.client.get(reverse('leads:dashboard'))
        self.assertEqual(response.status_code, 200)
