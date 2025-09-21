from django.urls import path

from .views import LeadCNPJLookupAPIView, LeadListCreateAPIView, LeadRetrieveUpdateAPIView

app_name = 'leads-api'

urlpatterns = [
    path('leads/', LeadListCreateAPIView.as_view(), name='lead-list-create'),
    path('leads/<int:pk>/', LeadRetrieveUpdateAPIView.as_view(), name='lead-detail'),
    path('leads/lookup-cnpj/', LeadCNPJLookupAPIView.as_view(), name='cnpj-lookup'),
]
