# ----------------------------------------------------------------------
# get_current_user dependencies
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from fastapi import Header, HTTPException
from fastapi.security import SecurityScopes

# NOC modules
from noc.aaa.models.user import User


def get_current_user(remote_user: Optional[str] = Header(None, alias="Remote-User")) -> User:
    """
    Get request current user

    :param remote_user:
    :return:
    """
    if not remote_user:
        raise HTTPException(403, "Not authorized")
    user = User.get_by_username(remote_user)
    if not user:
        raise HTTPException(403, "Not authorized")
    if not user.is_active:
        raise HTTPException(403, "Not authorized")
    return user


def get_user_scope(
    scopes: SecurityScopes, remote_user: Optional[str] = Header(None, alias="Remote-User")
) -> User:
    """
    Get request current user, when having scope access

    :param scopes:
    :param remote_user:
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
