from backend.smart_buy.providers.base import BaseProvider
from backend.smart_buy.providers.amazon import AmazonProvider
from backend.smart_buy.providers.flipkart import FlipkartProvider
from backend.smart_buy.providers.croma import CromaProvider
from backend.smart_buy.providers.reliance_digital import RelianceDigitalProvider
from backend.smart_buy.providers.tatacliq import TataCLiQProvider
from backend.smart_buy.providers.myntra import MyntraProvider

PROVIDER_REGISTRY = {
    'amazon': AmazonProvider,
    'flipkart': FlipkartProvider,
    'croma': CromaProvider,
    'reliance_digital': RelianceDigitalProvider,
    'tatacliq': TataCLiQProvider,
    'myntra': MyntraProvider,
}

def get_all_providers():
    return [cls() for cls in PROVIDER_REGISTRY.values()]

def get_provider(slug: str):
    cls = PROVIDER_REGISTRY.get(slug)
    return cls() if cls else None

__all__ = [
    'BaseProvider', 'PROVIDER_REGISTRY', 'get_all_providers', 'get_provider'
]

