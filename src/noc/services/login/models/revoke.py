# ----------------------------------------------------------------------
# RevokeRequest
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel


class RevokeRequest(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
