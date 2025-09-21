from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from integrations.receita_federal import ReceitaFederalClient

from .forms import (
    LeadCommercialForm,
    LeadDocumentsForm,
    LeadForm,
    LeadIndividualForm,
    LeadLegalEntityForm,
)
from .models import Lead
from .serializers import LeadSerializer


class LeadDashboardView(LoginRequiredMixin, View):
    template_name = 'leads/lead_list.html'
    login_url = 'admin:login'

    def get(self, request):
        lead_form = LeadForm(user=request.user)
        pf_form = LeadIndividualForm(prefix='pf')
        pj_form = LeadLegalEntityForm(prefix='pj')
        commercial_form = LeadCommercialForm(prefix='commercial')
        documents_form = LeadDocumentsForm(prefix='documents', person_type=Lead.PersonType.LEGAL_ENTITY)
        leads = Lead.objects.select_related(
            'representative',
            'individual',
            'legal_entity',
            'commercial',
        )
        context = {
            'lead_form': lead_form,
            'pf_form': pf_form,
            'pj_form': pj_form,
            'commercial_form': commercial_form,
            'documents_form': documents_form,
            'leads': leads,
            'cnpj_lookup_url': reverse('leads-api:cnpj-lookup'),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        person_type = request.POST.get('person_type')
        lead_form = LeadForm(request.POST, user=request.user)
        pf_data = request.POST if person_type == Lead.PersonType.INDIVIDUAL else None
        pj_data = request.POST if person_type == Lead.PersonType.LEGAL_ENTITY else None
        pf_form = LeadIndividualForm(pf_data, prefix='pf')
        pj_form = LeadLegalEntityForm(pj_data, prefix='pj')
        commercial_form = LeadCommercialForm(request.POST, prefix='commercial')
        documents_form = LeadDocumentsForm(
            request.POST,
            request.FILES,
            prefix='documents',
            person_type=person_type,
        )

        forms_valid = lead_form.is_valid()
        identification_valid = False
        if person_type == Lead.PersonType.INDIVIDUAL:
            identification_valid = pf_form.is_valid()
        elif person_type == Lead.PersonType.LEGAL_ENTITY:
            identification_valid = pj_form.is_valid()
        else:
            lead_form.add_error('person_type', 'Selecione o tipo de pessoa do lead.')
        commercial_valid = commercial_form.is_valid()
        documents_valid = documents_form.is_valid()

        if forms_valid and identification_valid and commercial_valid and documents_valid:
            lead = lead_form.save()
            if person_type == Lead.PersonType.INDIVIDUAL:
                individual = pf_form.save(commit=False)
                individual.lead = lead
                individual.save()
            else:
                legal_entity = pj_form.save(commit=False)
                legal_entity.lead = lead
                legal_entity.save()

            commercial = commercial_form.save(commit=False)
            commercial.lead = lead
            commercial.save()

            documents = documents_form.save(commit=False)
            documents.lead = lead
            documents.save()

            messages.success(request, 'Lead cadastrado com sucesso!')
            return redirect(reverse('leads:dashboard'))

        leads = Lead.objects.select_related(
            'representative',
            'individual',
            'legal_entity',
            'commercial',
        )
        messages.error(request, 'Verifique os dados do formulário.')
        context = {
            'lead_form': lead_form,
            'pf_form': pf_form,
            'pj_form': pj_form,
            'commercial_form': commercial_form,
            'documents_form': documents_form,
            'leads': leads,
            'cnpj_lookup_url': reverse('leads-api:cnpj-lookup'),
        }
        return render(request, self.template_name, context)


class LeadListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class LeadRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class LeadCNPJLookupAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cnpj = request.query_params.get('cnpj')
        if not cnpj:
            return Response({'detail': 'Informe o CNPJ para realizar a consulta.'}, status=status.HTTP_400_BAD_REQUEST)

        client = ReceitaFederalClient()
        try:
            data = client.get_company_data(cnpj)
        except Exception as exc:  # pragma: no cover - fallback para erros externos
            return Response({'detail': f'Não foi possível consultar a Receita Federal: {exc}'}, status=status.HTTP_502_BAD_GATEWAY)

        if not data:
            return Response({'detail': 'Nenhum dado encontrado para o CNPJ informado.'}, status=status.HTTP_404_NOT_FOUND)

        normalized = {
            'cnpj': data.get('cnpj', cnpj),
            'company_name': data.get('nome_fantasia') or data.get('nome') or data.get('razao_social') or '',
            'legal_name': data.get('razao_social') or data.get('nome') or '',
            'cep': data.get('cep', ''),
            'state': data.get('uf') or data.get('estado', ''),
            'city': data.get('municipio') or data.get('cidade', ''),
            'street': data.get('logradouro') or data.get('endereco', ''),
            'number': data.get('numero', ''),
            'complement': data.get('complemento', ''),
            'neighborhood': data.get('bairro', ''),
        }
        return Response({'data': normalized})
