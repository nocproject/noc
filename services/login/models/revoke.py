# ----------------------------------------------------------------------
# RevokeRequest
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from pydantic import BaseModel


class RevokeRequest(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
