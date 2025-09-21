from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'company_name',
        'email',
        'phone',
        'status',
        'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'company_name', 'cnpj')
    ordering = ('-created_at',)
