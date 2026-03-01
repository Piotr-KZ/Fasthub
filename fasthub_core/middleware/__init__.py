"""
Middleware package
Request logging and other HTTP middleware
"""

from fasthub_core.middleware.request_logging import RequestLoggingMiddleware

__all__ = ["RequestLoggingMiddleware"]
