"""
Tata CLiQ provider for Smart Buy.
Tata CLiQ does not provide a public product API.
Provider is marked unavailable until an official API is made available.
"""
from typing import List
from backend.smart_buy.providers.base import BaseProvider


class TataCLiQProvider(BaseProvider):
    platform_id = "tatacliq"
    platform_name = "Tata CLiQ"
    website_url = "https://www.tatacliq.com"
    logo_emoji = "🟣"

    def is_available(self) -> bool:
        return False

    def availability_message(self) -> str:
        return (
            "Tata CLiQ does not provide a public product API. "
            "Visit tatacliq.com directly for live prices."
        )

    def search(self, query: str, **filters) -> List[dict]:
        return []

