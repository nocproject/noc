# ----------------------------------------------------------------------
# Models for JSON-RPC API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pydantic import BaseModel


class JSONRemoteProcedureCall(BaseModel):
    method: str
    params: list
    id: int
