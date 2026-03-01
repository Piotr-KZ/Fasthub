"""
FastHub Core — uniwersalny fundament SaaS.
Instalacja: pip install fasthub-core
Użycie: from fasthub_core.auth import create_access_token
"""

__version__ = "2.0.0-alpha"

# Główne eksporty — to co inne aplikacje najczęściej potrzebują
from fasthub_core.config import Settings, get_settings
from fasthub_core.db.session import get_db, get_engine

__all__ = ["Settings", "get_settings", "get_db", "get_engine", "__version__"]
