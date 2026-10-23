# ----------------------------------------------------------------------
# StatusResponse
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: bool
    message: str | None = None


class StatusResponseError(BaseModel):
    error: str | None = None
    error_description: str | None = None
