from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def lead_document_upload_to(instance: 'LeadDocuments', filename: str) -> str:
    """Define um caminho organizado para os uploads de documentos de leads."""

    return f"leads/{instance.lead_id}/{filename}"


class Lead(models.Model):
    class LeadStatus(models.TextChoices):
        NEW = 'new', 'Novo'
        CONTACTED = 'contacted', 'Contato Realizado'
        QUALIFIED = 'qualified', 'Qualificado'
        PROPOSAL = 'proposal', 'Proposta Enviada'
        WON = 'won', 'Ganho'
        LOST = 'lost', 'Perdido'

    class PersonType(models.TextChoices):
        INDIVIDUAL = 'pf', 'Pessoa Física'
        LEGAL_ENTITY = 'pj', 'Pessoa Jurídica'

    representative = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Representante de Vendas',
        related_name='leads',
        on_delete=models.PROTECT,
    )
    person_type = models.CharField(
        'Tipo de Pessoa',
        max_length=2,
        choices=PersonType.choices,
    )
    status = models.CharField(
        'Status',
        max_length=32,
        choices=LeadStatus.choices,
        default=LeadStatus.NEW,
    )
    source = models.CharField('Origem', max_length=255, blank=True)
    notes = models.TextField('Anotações', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

    def __str__(self) -> str:  # pragma: no cover - representação simples
        return f"{self.display_name} ({self.get_person_type_display()})"

    @property
    def identification(self) -> LeadIndividual | LeadLegalEntity | None:
        if self.person_type == self.PersonType.INDIVIDUAL:
            return getattr(self, 'individual', None)
        if self.person_type == self.PersonType.LEGAL_ENTITY:
            return getattr(self, 'legal_entity', None)
        return None

    @property
    def display_name(self) -> str:
        identification = self.identification
        if not identification:
            return 'Lead sem identificação'
        if isinstance(identification, LeadIndividual):
            return identification.full_name
        return identification.company_name


class LeadIndividual(models.Model):
    lead = models.OneToOneField(
        Lead,
        verbose_name='Lead',
        related_name='individual',
        on_delete=models.CASCADE,
    )
    full_name = models.CharField('Nome', max_length=255)
    cpf = models.CharField('CPF', max_length=14)
    rg = models.CharField('RG', max_length=20, blank=True)
    cep = models.CharField('CEP', max_length=9)
    state = models.CharField('Estado', max_length=2)
    city = models.CharField('Cidade', max_length=128)
    street = models.CharField('Endereço', max_length=255)
    number = models.CharField('Número', max_length=20)
    complement = models.CharField('Complemento', max_length=255, blank=True)
    neighborhood = models.CharField('Bairro', max_length=128)
    phone = models.CharField('Telefone', max_length=32)
    email = models.EmailField('E-mail')

    class Meta:
        verbose_name = 'Pessoa Física'
        verbose_name_plural = 'Pessoas Físicas'

    def __str__(self) -> str:  # pragma: no cover - representação simples
        return self.full_name


class LeadLegalEntity(models.Model):
    lead = models.OneToOneField(
        Lead,
        verbose_name='Lead',
        related_name='legal_entity',
        on_delete=models.CASCADE,
    )
    cnpj = models.CharField('CNPJ', max_length=18)
    company_name = models.CharField('Nome da Empresa', max_length=255)
    legal_name = models.CharField('Razão Social', max_length=255)
    cep = models.CharField('CEP', max_length=9)
    state = models.CharField('Estado', max_length=2)
    city = models.CharField('Cidade', max_length=128)
    street = models.CharField('Endereço', max_length=255)
    number = models.CharField('Número', max_length=20)
    complement = models.CharField('Complemento', max_length=255, blank=True)
    neighborhood = models.CharField('Bairro', max_length=128)

    class Meta:
        verbose_name = 'Pessoa Jurídica'
        verbose_name_plural = 'Pessoas Jurídicas'

    def __str__(self) -> str:  # pragma: no cover - representação simples
        return self.company_name


class LeadCommercialInfo(models.Model):
    lead = models.OneToOneField(
        Lead,
        verbose_name='Lead',
        related_name='commercial',
        on_delete=models.CASCADE,
    )
    energy_customer_number = models.CharField('Número do Cliente', max_length=64)
    energy_provider = models.CharField('Concessionária', max_length=128)
    last_energy_bill_amount = models.DecimalField(
        'Valor da Última Conta de Luz',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    bill_due_date = models.DateField('Data de Vencimento da Fatura')
    seller_discount = models.DecimalField(
        'Desconto do Vendedor (%)',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Informe o desconto acordado em percentual.',
    )

    class Meta:
        verbose_name = 'Dado Comercial'
        verbose_name_plural = 'Dados Comerciais'

    def __str__(self) -> str:  # pragma: no cover - representação simples
        return f"Concessionária {self.energy_provider}"


class LeadDocuments(models.Model):
    lead = models.OneToOneField(
        Lead,
        verbose_name='Lead',
        related_name='documents',
        on_delete=models.CASCADE,
    )
    id_document_front = models.FileField(
        'RG (frente)',
        upload_to=lead_document_upload_to,
    )
    id_document_back = models.FileField(
        'RG (verso)',
        upload_to=lead_document_upload_to,
    )
    energy_bill = models.FileField(
        'Fatura de Energia',
        upload_to=lead_document_upload_to,
    )
    articles_of_association = models.FileField(
        'Contrato Social',
        upload_to=lead_document_upload_to,
        blank=True,
    )
    cnpj_card = models.FileField(
        'Cartão CNPJ',
        upload_to=lead_document_upload_to,
        blank=True,
    )

    class Meta:
        verbose_name = 'Documento do Lead'
        verbose_name_plural = 'Documentos do Lead'

    def __str__(self) -> str:  # pragma: no cover - representação simples
        return f"Documentos do lead {self.lead_id}"
