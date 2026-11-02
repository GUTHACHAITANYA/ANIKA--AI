"""
Reliance Digital provider for Smart Buy.
Reliance Digital does not provide a public product API.
Provider is marked unavailable until an official API is made available.
"""
from typing import List
from backend.smart_buy.providers.base import BaseProvider


class RelianceDigitalProvider(BaseProvider):
    platform_id = "reliance_digital"
    platform_name = "Reliance Digital"
    website_url = "https://www.reliancedigital.in"
    logo_emoji = "🔴"

    def is_available(self) -> bool:
        return False

    def availability_message(self) -> str:
        return (
            "Reliance Digital does not provide a public product API. "
            "Visit reliancedigital.in directly for live prices."
        )

    def search(self, query: str, **filters) -> List[dict]:
        return []

