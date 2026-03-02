"""
Token Administration Endpoints
Admin endpoints for managing token blacklist
"""

from datetime import timedelta

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_admin_user
from app.models.user import User
from fasthub_core.auth.blacklist import get_blacklist, blacklist_token

router = APIRouter()


@router.get("/blacklist/stats")
async def get_blacklist_stats(current_user: User = Depends(get_current_admin_user)):
    """
    Get token blacklist statistics

    Requires admin privileges.
    """
    bl = await get_blacklist()
    return {
        "backend": type(bl).__name__,
        "status": "connected",
    }


@router.post("/blacklist/clear")
async def clear_blacklist(current_user: User = Depends(get_current_admin_user)):
    """
    Clear all blacklisted tokens

    Requires admin privileges.
    Use with caution - this will allow all previously revoked tokens to be used again.
    """
    bl = await get_blacklist()
    # Redis: flush by prefix; InMemory: clear dict
    if hasattr(bl, '_blacklist'):
        bl._blacklist.clear()
        return {"message": "Token blacklist cleared successfully", "cleared": True}
    elif hasattr(bl, 'redis'):
        try:
            keys = await bl.redis.keys(f"{bl.prefix}*")
            if keys:
                await bl.redis.delete(*keys)
            return {"message": "Token blacklist cleared successfully", "cleared": True}
        except Exception:
            return {"message": "Failed to clear token blacklist (Redis error)", "cleared": False}
    return {"message": "Unknown blacklist backend", "cleared": False}


@router.post("/revoke-token")
async def revoke_token(token: str, current_user: User = Depends(get_current_admin_user)):
    """
    Manually revoke a specific token

    Requires admin privileges.
    """
    expires_in = int(timedelta(days=7).total_seconds())
    await blacklist_token(token, expires_in)
    return {"message": "Token revoked successfully", "revoked": True}
