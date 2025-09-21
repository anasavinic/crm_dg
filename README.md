# CRM Django

Projeto inicial de um CRM interno construído com Django e Django REST Framework para gestão de leads.

## Estrutura

- **Frontend**: Templates Django com layout responsivo e cores padronizadas.
- **Backend**: Django + DRF com modelo de Lead, API REST e painel web básico.
- **Integrações**: Clients para Receita Federal e Autentique com placeholders para credenciais.

## Requisitos

- Python 3.11+
- Django 4.2+
- Django REST Framework 3.14+

Instale as dependências executando `pip install -r requirements.txt`.

## Configuração

1. Configure as variáveis de ambiente para as integrações:
   - `RECEITA_FEDERAL_BASE_URL`
   - `RECEITA_FEDERAL_TOKEN`
   - `AUTENTIQUE_BASE_URL`
   - `AUTENTIQUE_TOKEN`
2. Execute as migrações: `python manage.py migrate`.
3. Crie um superusuário: `python manage.py createsuperuser`.
4. Inicie o servidor: `python manage.py runserver`.

## API

- `GET /api/leads/` — lista os leads cadastrados.
- `POST /api/leads/` — cria um novo lead.
- `GET /api/leads/<id>/` — detalhes de um lead.
- `PUT/PATCH /api/leads/<id>/` — atualiza um lead existente.

## Próximos Passos

- Definição e criação do banco de dados em produção.
- Implementação das integrações externas com autenticação segura.
- Refinamento dos fluxos de funil e dashboards personalizados.
