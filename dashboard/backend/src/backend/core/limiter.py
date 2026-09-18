
"""
Shared rate limiter (slowapi, backed by in-memory storage by default).
One Limiter instance imported by main.py and any router that needs
per-endpoint limits — sharing the instance is required for slowapi's
state to be consistent across the app.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
