from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Lead, LeadIndividual, LeadLegalEntity


class LeadModelTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username='vendedor', password='senha-segura')

    def test_display_name_for_individual(self):
        lead = Lead.objects.create(
            representative=self.user,
            person_type=Lead.PersonType.INDIVIDUAL,
        )
        LeadIndividual.objects.create(
            lead=lead,
            full_name='Fulano da Silva',
            cpf='123.456.789-00',
            rg='12.345.678-9',
            cep='12345-000',
            state='SP',
            city='São Paulo',
            street='Rua Teste',
            number='100',
            complement='',
            neighborhood='Centro',
            phone='11999999999',
            email='fulano@example.com',
        )

        self.assertEqual(lead.display_name, 'Fulano da Silva')
        self.assertIn('Pessoa Física', str(lead))

    def test_display_name_for_legal_entity(self):
        lead = Lead.objects.create(
            representative=self.user,
            person_type=Lead.PersonType.LEGAL_ENTITY,
        )
        LeadLegalEntity.objects.create(
            lead=lead,
            cnpj='12.345.678/0001-90',
            company_name='Empresa Teste',
            legal_name='Empresa Teste LTDA',
            cep='12345-000',
            state='SP',
            city='São Paulo',
            street='Av. Principal',
            number='200',
            complement='',
            neighborhood='Centro',
        )

        self.assertEqual(lead.display_name, 'Empresa Teste')
        self.assertIn('Pessoa Jurídica', str(lead))


class LeadDashboardViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username='gestor', password='senha-123')

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse('leads:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.headers['Location'])

    def test_can_create_individual_lead(self):
        self.client.login(username='gestor', password='senha-123')
        url = reverse('leads:dashboard')
        post_data = {
            'person_type': Lead.PersonType.INDIVIDUAL,
            'status': Lead.LeadStatus.NEW,
            'source': 'Indicação',
            'notes': 'Lead de teste automatizado.',
            'pf-full_name': 'Maria Joaquina',
            'pf-cpf': '987.654.321-00',
            'pf-rg': '98.765.432-1',
            'pf-cep': '01001-000',
            'pf-state': 'SP',
            'pf-city': 'São Paulo',
            'pf-street': 'Rua das Flores',
            'pf-number': '500',
            'pf-complement': '',
            'pf-neighborhood': 'Centro',
            'pf-phone': '11988887777',
            'pf-email': 'maria@example.com',
            'commercial-energy_customer_number': '123456',
            'commercial-energy_provider': 'Enel',
            'commercial-last_energy_bill_amount': '350.75',
            'commercial-bill_due_date': '2024-01-15',
            'commercial-seller_discount': '5.50',
        }
        file_payload = {
            'documents-id_document_front': SimpleUploadedFile('rg_frente.pdf', b'PDF'),
            'documents-id_document_back': SimpleUploadedFile('rg_verso.pdf', b'PDF'),
            'documents-energy_bill': SimpleUploadedFile('conta.pdf', b'PDF'),
        }

        response = self.client.post(url, {**post_data, **file_payload}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 1)
        lead = Lead.objects.first()
        self.assertEqual(lead.person_type, Lead.PersonType.INDIVIDUAL)
        self.assertTrue(hasattr(lead, 'individual'))
