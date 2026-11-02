"""
Croma provider for Smart Buy.
Croma does not provide a public product API.
Provider is marked unavailable until an official API is made available.
"""
from typing import List
from backend.smart_buy.providers.base import BaseProvider


class CromaProvider(BaseProvider):
    platform_id = "croma"
    platform_name = "Croma"
    website_url = "https://www.croma.com"
    logo_emoji = "🔵"

    def is_available(self) -> bool:
        return False

    def availability_message(self) -> str:
        return (
            "Croma does not provide a public product API. "
            "Visit croma.com directly for live prices."
        )

    def search(self, query: str, **filters) -> List[dict]:
        return []

