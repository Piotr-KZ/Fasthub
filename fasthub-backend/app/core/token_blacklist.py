"""
Token Blacklist — thin wrapper re-exporting from fasthub_core.auth.blacklist

Source of truth: fasthub_core/auth/blacklist.py (async, JTI-based)
"""

from fasthub_core.auth.blacklist import (
    blacklist_token,
    is_token_blacklisted,
    get_blacklist,
    BlacklistBackend,
    RedisBlacklist,
    InMemoryBlacklist,
)

__all__ = [
    "blacklist_token",
    "is_token_blacklisted",
    "get_blacklist",
    "BlacklistBackend",
    "RedisBlacklist",
    "InMemoryBlacklist",
]
