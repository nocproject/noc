# ----------------------------------------------------------------------
# /api/ui/avatar endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response

# NOC modules
from noc.config import config
from noc.aaa.models.user import User
from noc.core.service.deps.user import get_current_user
from noc.main.models.avatar import Avatar
from noc.core.comp import smart_bytes
from noc.core.ioloop.util import run_sync
from noc.core.mime import ContentType
from ..models.status import StatusResponse

router = APIRouter()


@router.get("/api/ui/avatar/{user_id}", tags=["ui", "avatar"])
def get_avatar(user_id: str, _: User = Depends(get_current_user)):
    avatar = Avatar.objects.filter(user_id=str(user_id)).first()
    if not avatar:
        raise HTTPException(status_code=404)
    return Response(
        content=avatar.data,
        media_type=avatar.get_content_type(),
    )


@router.post("/api/ui/avatar", response_model=StatusResponse, tags=["ui", "avatar"])
def save_avatar(user: User = Depends(get_current_user), image: UploadFile = File(...)):
    async def read_file() -> bytes:
        return smart_bytes(await image.read(config.ui.max_avatar_size + 1))

    data = run_sync(read_file)
    if len(data) > config.ui.max_avatar_size:
        raise HTTPException(status_code=413)
    content_type = ContentType.from_content_type(image.content_type)
    if content_type is None:
        raise HTTPException(status_code=421)
    avatar = Avatar.objects.filter(user_id=str(user.id)).first()
    if avatar:
        # Update
        avatar.data = data
        avatar.content_type = content_type
    else:
        # Create
        avatar = Avatar(user_id=str(user.id), data=data, content_type=content_type)
    avatar.save()
    return StatusResponse(status=True)


@router.delete("/api/ui/avatar", response_model=StatusResponse, tags=["ui", "avatar"])
def delete_avatar(
    user: User = Depends(get_current_user),
):
    avatar = Avatar.objects.filter(user_id=str(user.id)).first()
    if avatar:
        avatar.delete()
    return StatusResponse(status=True)
