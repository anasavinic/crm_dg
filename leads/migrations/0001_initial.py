# Generated manually because Django is not available in the execution environment.
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person_type', models.CharField(choices=[('pf', 'Pessoa Física'), ('pj', 'Pessoa Jurídica')], max_length=2, verbose_name='Tipo de Pessoa')),
                ('status', models.CharField(choices=[('new', 'Novo'), ('contacted', 'Contato Realizado'), ('qualified', 'Qualificado'), ('proposal', 'Proposta Enviada'), ('won', 'Ganho'), ('lost', 'Perdido')], default='new', max_length=32, verbose_name='Status')),
                ('source', models.CharField(blank=True, max_length=255, verbose_name='Origem')),
                ('notes', models.TextField(blank=True, verbose_name='Anotações')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('representative', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='leads', to=settings.AUTH_USER_MODEL, verbose_name='Representante de Vendas')),
            ],
            options={
                'verbose_name': 'Lead',
                'verbose_name_plural': 'Leads',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='LeadCommercialInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('energy_customer_number', models.CharField(max_length=64, verbose_name='Número do Cliente')),
                ('energy_provider', models.CharField(max_length=128, verbose_name='Concessionária')),
                ('last_energy_bill_amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(0)], verbose_name='Valor da Última Conta de Luz')),
                ('bill_due_date', models.DateField(verbose_name='Data de Vencimento da Fatura')),
                ('seller_discount', models.DecimalField(decimal_places=2, help_text='Informe o desconto acordado em percentual.', max_digits=5, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Desconto do Vendedor (%)')),
                ('lead', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='commercial', to='leads.lead', verbose_name='Lead')),
            ],
            options={
                'verbose_name': 'Dado Comercial',
                'verbose_name_plural': 'Dados Comerciais',
            },
        ),
        migrations.CreateModel(
            name='LeadDocuments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_document_front', models.FileField(upload_to='leads.models.lead_document_upload_to', verbose_name='RG (frente)')),
                ('id_document_back', models.FileField(upload_to='leads.models.lead_document_upload_to', verbose_name='RG (verso)')),
                ('energy_bill', models.FileField(upload_to='leads.models.lead_document_upload_to', verbose_name='Fatura de Energia')),
                ('articles_of_association', models.FileField(blank=True, upload_to='leads.models.lead_document_upload_to', verbose_name='Contrato Social')),
                ('cnpj_card', models.FileField(blank=True, upload_to='leads.models.lead_document_upload_to', verbose_name='Cartão CNPJ')),
                ('lead', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='leads.lead', verbose_name='Lead')),
            ],
            options={
                'verbose_name': 'Documento do Lead',
                'verbose_name_plural': 'Documentos do Lead',
            },
        ),
        migrations.CreateModel(
            name='LeadLegalEntity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cnpj', models.CharField(max_length=18, verbose_name='CNPJ')),
                ('company_name', models.CharField(max_length=255, verbose_name='Nome da Empresa')),
                ('legal_name', models.CharField(max_length=255, verbose_name='Razão Social')),
                ('cep', models.CharField(max_length=9, verbose_name='CEP')),
                ('state', models.CharField(max_length=2, verbose_name='Estado')),
                ('city', models.CharField(max_length=128, verbose_name='Cidade')),
                ('street', models.CharField(max_length=255, verbose_name='Endereço')),
                ('number', models.CharField(max_length=20, verbose_name='Número')),
                ('complement', models.CharField(blank=True, max_length=255, verbose_name='Complemento')),
                ('neighborhood', models.CharField(max_length=128, verbose_name='Bairro')),
                ('lead', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='legal_entity', to='leads.lead', verbose_name='Lead')),
            ],
            options={
                'verbose_name': 'Pessoa Jurídica',
                'verbose_name_plural': 'Pessoas Jurídicas',
            },
        ),
        migrations.CreateModel(
            name='LeadIndividual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name='Nome')),
                ('cpf', models.CharField(max_length=14, verbose_name='CPF')),
                ('rg', models.CharField(blank=True, max_length=20, verbose_name='RG')),
                ('cep', models.CharField(max_length=9, verbose_name='CEP')),
                ('state', models.CharField(max_length=2, verbose_name='Estado')),
                ('city', models.CharField(max_length=128, verbose_name='Cidade')),
                ('street', models.CharField(max_length=255, verbose_name='Endereço')),
                ('number', models.CharField(max_length=20, verbose_name='Número')),
                ('complement', models.CharField(blank=True, max_length=255, verbose_name='Complemento')),
                ('neighborhood', models.CharField(max_length=128, verbose_name='Bairro')),
                ('phone', models.CharField(max_length=32, verbose_name='Telefone')),
                ('email', models.EmailField(max_length=254, verbose_name='E-mail')),
                ('lead', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='individual', to='leads.lead', verbose_name='Lead')),
            ],
            options={
                'verbose_name': 'Pessoa Física',
                'verbose_name_plural': 'Pessoas Físicas',
            },
        ),
    ]
