# ----------------------------------------------------------------------
# StatusResponse
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel


class ErrorItem(BaseModel):
    message: str


class StatusResponse(BaseModel):
    status: bool
    errors: list[ErrorItem] | None = None
