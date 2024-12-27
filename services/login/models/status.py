# ----------------------------------------------------------------------
# StatusResponse
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: bool
    message: Optional[str] = None


class StatusResponseError(BaseModel):
    error: Optional[str] = None
    error_description: Optional[str] = None
