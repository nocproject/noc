# ----------------------------------------------------------------------
# Models for JSON-RPC API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any

# Third-party modules
from pydantic import BaseModel


class JSONRemoteProcedureCall(BaseModel):
    method: str
    params: list[Any]
    id: int


class JSONRPCResponse(BaseModel):
    result: Any
    error: Any
    id: int
