from django.contrib import admin

from .models import (
    Lead,
    LeadCommercialInfo,
    LeadDocuments,
    LeadIndividual,
    LeadLegalEntity,
)


class LeadIndividualInline(admin.StackedInline):
    model = LeadIndividual
    extra = 0
    can_delete = False


class LeadLegalEntityInline(admin.StackedInline):
    model = LeadLegalEntity
    extra = 0
    can_delete = False


class LeadCommercialInline(admin.StackedInline):
    model = LeadCommercialInfo
    extra = 0
    can_delete = False


class LeadDocumentsInline(admin.StackedInline):
    model = LeadDocuments
    extra = 0
    can_delete = False


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'get_person_type_display',
        'representative',
        'status',
        'created_at',
    )
    list_filter = ('status', 'person_type', 'created_at')
    search_fields = (
        'individual__full_name',
        'individual__cpf',
        'legal_entity__company_name',
        'legal_entity__cnpj',
        'representative__username',
    )
    ordering = ('-created_at',)

    def get_inlines(self, request, obj=None):
        inlines = [LeadCommercialInline, LeadDocumentsInline]
        if obj:
            if obj.person_type == Lead.PersonType.INDIVIDUAL:
                inlines.insert(0, LeadIndividualInline)
            else:
                inlines.insert(0, LeadLegalEntityInline)
        else:
            # Na criação exibe ambos para facilitar preenchimento rápido.
            inlines.insert(0, LeadIndividualInline)
            inlines.insert(1, LeadLegalEntityInline)
        return inlines
