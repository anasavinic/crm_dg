from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from rest_framework import generics, permissions

from .forms import LeadForm
from .models import Lead
from .serializers import LeadSerializer


class LeadDashboardView(View):
    template_name = 'leads/lead_list.html'

    def get(self, request):
        form = LeadForm()
        leads = Lead.objects.all()
        return render(request, self.template_name, {'form': form, 'leads': leads})

    def post(self, request):
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead cadastrado com sucesso!')
            return redirect(reverse('leads:dashboard'))
        leads = Lead.objects.all()
        messages.error(request, 'Verifique os dados do formulário.')
        return render(request, self.template_name, {'form': form, 'leads': leads})


class LeadListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class LeadRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
