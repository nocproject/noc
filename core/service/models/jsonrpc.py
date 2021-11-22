# ----------------------------------------------------------------------
# Models for JSON-RPC API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, List

# Third-party modules
from pydantic import BaseModel


class JSONRemoteProcedureCall(BaseModel):
    method: str
    params: List[Any]
    id: int
