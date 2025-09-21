from django.urls import path

from .views import LeadDashboardView

app_name = 'leads'

urlpatterns = [
    path('', LeadDashboardView.as_view(), name='dashboard'),
]
