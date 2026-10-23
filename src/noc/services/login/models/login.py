# ----------------------------------------------------------------------
# LoginRequest
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pydantic import BaseModel


class LoginRequest(BaseModel):
    user: str
    password: str
