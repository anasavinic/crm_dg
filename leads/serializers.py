from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Lead, LeadCommercialInfo, LeadDocuments, LeadIndividual, LeadLegalEntity


class LeadIndividualSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadIndividual
        exclude = ['lead']


class LeadLegalEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadLegalEntity
        exclude = ['lead']


class LeadCommercialInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadCommercialInfo
        exclude = ['lead']


class LeadDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadDocuments
        exclude = ['lead']


class LeadSerializer(serializers.ModelSerializer):
    representative = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        required=False,
        default=serializers.CurrentUserDefault(),
    )
    representative_name = serializers.CharField(source='representative.get_full_name', read_only=True)
    individual = LeadIndividualSerializer(required=False)
    legal_entity = LeadLegalEntitySerializer(required=False)
    commercial = LeadCommercialInfoSerializer(required=False)
    documents = LeadDocumentsSerializer(required=False)
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id',
            'representative',
            'representative_name',
            'person_type',
            'status',
            'source',
            'notes',
            'display_name',
            'individual',
            'legal_entity',
            'commercial',
            'documents',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'display_name', 'created_at', 'updated_at']

    def validate(self, attrs):
        person_type = attrs.get('person_type') or getattr(self.instance, 'person_type', None)
        has_individual_payload = 'individual' in attrs
        has_legal_entity_payload = 'legal_entity' in attrs
        individual = attrs.get('individual')
        legal_entity = attrs.get('legal_entity')
        existing_individual = getattr(self.instance, 'individual', None) if self.instance else None
        existing_legal_entity = getattr(self.instance, 'legal_entity', None) if self.instance else None

        if person_type == Lead.PersonType.INDIVIDUAL:
            if has_individual_payload:
                if not individual:
                    raise serializers.ValidationError(
                        'Os dados da pessoa física são obrigatórios para o lead.'
                    )
            elif not existing_individual:
                raise serializers.ValidationError('Os dados da pessoa física são obrigatórios para o lead.')

        if person_type == Lead.PersonType.LEGAL_ENTITY:
            if has_legal_entity_payload:
                if not legal_entity:
                    raise serializers.ValidationError(
                        'Os dados da pessoa jurídica são obrigatórios para o lead.'
                    )
            elif not existing_legal_entity:
                raise serializers.ValidationError('Os dados da pessoa jurídica são obrigatórios para o lead.')

        attrs = super().validate(attrs)
        return self._ensure_representative(attrs)

    def _ensure_representative(self, attrs):
        representative = attrs.get('representative')
        request = self.context.get('request')
        if representative is None and request and request.user.is_authenticated:
            attrs['representative'] = request.user
        elif representative is None:
            raise serializers.ValidationError({'representative': 'Informe o representante responsável pelo lead.'})
        elif hasattr(representative, 'is_authenticated') and not representative.is_authenticated:
            raise serializers.ValidationError({'representative': 'Informe o representante responsável pelo lead.'})
        return attrs

    def create(self, validated_data):
        individual_data = validated_data.pop('individual', None)
        legal_entity_data = validated_data.pop('legal_entity', None)
        commercial_data = validated_data.pop('commercial', None)
        documents_data = validated_data.pop('documents', None)

        lead = Lead.objects.create(**validated_data)

        if lead.person_type == Lead.PersonType.INDIVIDUAL and individual_data:
            LeadIndividual.objects.create(lead=lead, **individual_data)
        elif lead.person_type == Lead.PersonType.LEGAL_ENTITY and legal_entity_data:
            LeadLegalEntity.objects.create(lead=lead, **legal_entity_data)

        if commercial_data:
            LeadCommercialInfo.objects.create(lead=lead, **commercial_data)

        if documents_data:
            LeadDocuments.objects.create(lead=lead, **documents_data)

        return lead

    def update(self, instance, validated_data):
        individual_data = validated_data.pop('individual', None)
        legal_entity_data = validated_data.pop('legal_entity', None)
        commercial_data = validated_data.pop('commercial', None)
        documents_data = validated_data.pop('documents', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if individual_data is not None:
            LeadIndividual.objects.update_or_create(lead=instance, defaults=individual_data)
        if legal_entity_data is not None:
            LeadLegalEntity.objects.update_or_create(lead=instance, defaults=legal_entity_data)
        if commercial_data is not None:
            LeadCommercialInfo.objects.update_or_create(lead=instance, defaults=commercial_data)
        if documents_data is not None:
            LeadDocuments.objects.update_or_create(lead=instance, defaults=documents_data)

        return instance
