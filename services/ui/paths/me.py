# ----------------------------------------------------------------------
# /api/ui/me endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter, Depends

# NOC modules
from noc.config import config
from noc.aaa.models.user import User
from noc.core.service.deps.user import get_current_user
from ..models.me import MeResponse, GroupItem

router = APIRouter()


@router.get("/api/ui/me", response_model=MeResponse, tags=["ui"])
def get_me(user: User = Depends(get_current_user)):
    return MeResponse(
        id=str(user.id),
        username=user.username,
        first_name=user.first_name or None,
        last_name=user.last_name or None,
        email=user.email or None,
        groups=[GroupItem(id=str(g.id), name=g.name) for g in user.groups.all()],
        language=user.preferred_language or config.language,
    )
