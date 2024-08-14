# ---------------------------------------------------------------------
# Controller model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional


@dataclass
class ControllerConfig(object):
    """
    Attributes:
        local_id: Identifier host on controller
        address: Controller address
        port: Controller port
        user: Username on controller for access
        password:
    """
    local_id: str
    address: str
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
