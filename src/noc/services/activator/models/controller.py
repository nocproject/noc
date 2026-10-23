# ---------------------------------------------------------------------
# Controller model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass


@dataclass
class ControllerConfig:
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
    global_id: int | None = None
    port: int | None = None
    user: str | None = None
    password: str | None = None
    api_key: str | None = None
