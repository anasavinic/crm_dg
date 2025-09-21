"""Cliente de integração com a plataforma Autentique."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from django.conf import settings


@dataclass
class AutentiqueClient:
    base_url: str | None = None
    token: str | None = None

    def __post_init__(self) -> None:
        if not self.base_url:
            self.base_url = settings.API_SETTINGS['autentique']['base_url']
        if not self.token:
            self.token = settings.API_SETTINGS['autentique']['token']

    def create_document(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.base_url or not self.token:
            raise RuntimeError('Credenciais da Autentique não configuradas.')

        response = requests.post(
            f"{self.base_url.rstrip('/')}/documents",
            headers={'Authorization': f"Bearer {self.token}"},
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
