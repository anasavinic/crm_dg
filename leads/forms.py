from __future__ import annotations

from django import forms

from .models import Lead, LeadCommercialInfo, LeadDocuments, LeadIndividual, LeadLegalEntity


class LeadForm(forms.ModelForm):
    representative = forms.CharField(
        label='Representante de Vendas',
        required=False,
        disabled=True,
    )

    class Meta:
        model = Lead
        fields = ['person_type', 'status', 'source', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated:
            display_name = self.user.get_full_name() or self.user.get_username()
            self.fields['representative'].initial = display_name
        if not self.data:
            self.fields['person_type'].initial = Lead.PersonType.LEGAL_ENTITY
        self.fields['person_type'].widget.attrs.update({'data-behaviour': 'person-type-select'})

    def clean(self):
        cleaned_data = super().clean()
        if not self.user or not self.user.is_authenticated:
            raise forms.ValidationError('É necessário estar autenticado para cadastrar um lead.')
        return cleaned_data

    def save(self, commit=True):
        lead = super().save(commit=False)
        lead.representative = self.user
        if commit:
            lead.save()
        return lead


class LeadIndividualForm(forms.ModelForm):
    class Meta:
        model = LeadIndividual
        exclude = ['lead']


class LeadLegalEntityForm(forms.ModelForm):
    class Meta:
        model = LeadLegalEntity
        exclude = ['lead']


class LeadCommercialForm(forms.ModelForm):
    class Meta:
        model = LeadCommercialInfo
        exclude = ['lead']
        widgets = {
            'bill_due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class LeadDocumentsForm(forms.ModelForm):
    class Meta:
        model = LeadDocuments
        exclude = ['lead']

    def __init__(self, *args, person_type: str | None = None, **kwargs):
        self.person_type = person_type or Lead.PersonType.LEGAL_ENTITY
        super().__init__(*args, **kwargs)
        self.fields['articles_of_association'].required = (
            self.person_type == Lead.PersonType.LEGAL_ENTITY
        )

    def clean(self):
        cleaned_data = super().clean()
        instance = getattr(self, 'instance', None)

        def has_file(field_name: str) -> bool:
            file_value = cleaned_data.get(field_name)
            if file_value:
                return True
            if file_value is False:  # ClearableFileInput retorna False quando não há novo upload.
                file_value = None
            if instance and getattr(instance, field_name):
                return True
            return False

        if self.person_type == Lead.PersonType.LEGAL_ENTITY and not has_file('articles_of_association'):
            self.add_error(
                'articles_of_association',
                'O Contrato Social é obrigatório para Pessoa Jurídica.',
            )
        for field_name in ('id_document_front', 'id_document_back', 'energy_bill'):
            if not has_file(field_name):
                self.add_error(field_name, 'Este documento é obrigatório.')
        return cleaned_data
