from django.db import models


class Lead(models.Model):
    class LeadStatus(models.TextChoices):
        NEW = 'new', 'Novo'
        CONTACTED = 'contacted', 'Contato Realizado'
        QUALIFIED = 'qualified', 'Qualificado'
        PROPOSAL = 'proposal', 'Proposta Enviada'
        WON = 'won', 'Ganho'
        LOST = 'lost', 'Perdido'

    name = models.CharField('Nome', max_length=255)
    email = models.EmailField('E-mail', blank=True)
    phone = models.CharField('Telefone', max_length=32, blank=True)
    company_name = models.CharField('Empresa', max_length=255, blank=True)
    cnpj = models.CharField('CNPJ', max_length=18, blank=True)
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

    def __str__(self) -> str:
        return f"{self.name} ({self.company_name or 'Pessoa Física'})"
