# ----------------------------------------------------------------------
# get_current_user dependencies
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from urllib.parse import unquote

# Third-party modules
from fastapi import Header, HTTPException
from fastapi.security import SecurityScopes

# NOC modules
from noc.aaa.models.user import User
from noc.core.service.loader import get_service

svc = get_service()


async def get_current_user(
    remote_user: str | None = Header(None, alias="Remote-User"),
) -> User | None:
    """
    Get request current user

    :return:
    """
    if not remote_user and not getattr(svc, "auth_required", False):
        return None
    if not remote_user:
        raise HTTPException(403, "Not authorized")
    user = User.get_by_username(unquote(remote_user))
    if not user:
        raise HTTPException(403, "Not authorized")
    if not user.is_active:
        raise HTTPException(403, "Not authorized")
    return user


def get_user_scope(
    scopes: SecurityScopes, remote_user: str | None = Header(None, alias="Remote-User")
) -> User:
    """
    Get request current user, when having scope access

    :return:
    """
    if not remote_user:
        raise HTTPException(403, "Not authorized")
    user = User.get_by_username(remote_user)
    if not user:
        raise HTTPException(403, "Not authorized")
    if not user.is_active:
        raise HTTPException(403, "Not authorized")
    # @todo: Check user's active scopes against {scopes.scopes}
    return user
