# ----------------------------------------------------------------------
# SetAdminRequest
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pydantic import BaseModel


class SetAdminRequest(BaseModel):
    user: str
    password: str
