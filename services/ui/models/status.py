# ----------------------------------------------------------------------
# StatusResponse
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel


class ErrorItem(BaseModel):
    message: str


class StatusResponse(BaseModel):
    status: bool
    errors: Optional[List[ErrorItem]] = None
