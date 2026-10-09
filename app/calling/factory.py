from app.calling.retell import RetellClient
from app.calling.vapi import VapiClient


def normalize_call_provider(provider: str) -> str:
    p = (provider or 'retell').lower()
    if p not in {'retell', 'vapi'}:
        raise ValueError('provider must be retell or vapi')
    return p


def get_call_client(provider: str):
    return RetellClient() if provider == 'retell' else VapiClient()
