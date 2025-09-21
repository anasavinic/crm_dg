"""Integração com a API da Receita Federal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from django.conf import settings


@dataclass
class ReceitaFederalClient:
    base_url: str | None = None
    token: str | None = None

    def __post_init__(self) -> None:
        if not self.base_url:
            self.base_url = settings.API_SETTINGS['receita_federal']['base_url']
        if not self.token:
            self.token = settings.API_SETTINGS['receita_federal']['token']

    def get_company_data(self, cnpj: str) -> dict[str, Any]:
        """Realiza a consulta de CNPJ na Receita Federal.

        Em ambientes de desenvolvimento, a integração pode retornar um dicionário
        vazio caso as credenciais não estejam configuradas.
        """

        if not self.base_url or not self.token:
            return {}

        response = requests.get(
            f"{self.base_url.rstrip('/')}/{cnpj}",
            headers={'Authorization': f"Bearer {self.token}"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
