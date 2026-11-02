"""
Myntra provider for Smart Buy.
Myntra does not provide a public product API.
Provider is marked unavailable until an official API is made available.
"""
from typing import List
from backend.smart_buy.providers.base import BaseProvider


class MyntraProvider(BaseProvider):
    platform_id = "myntra"
    platform_name = "Myntra"
    website_url = "https://www.myntra.com"
    logo_emoji = "👗"

    def is_available(self) -> bool:
        return False

    def availability_message(self) -> str:
        return (
            "Myntra does not provide a public product API. "
            "Visit myntra.com directly for live prices."
        )

    def search(self, query: str, **filters) -> List[dict]:
        return []

