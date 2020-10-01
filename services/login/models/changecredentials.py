# ----------------------------------------------------------------------
# ChangeCredentialsRequest
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pydantic import BaseModel


class ChangeCredentialsRequest(BaseModel):
    user: str
    old_password: str
    new_password: str
