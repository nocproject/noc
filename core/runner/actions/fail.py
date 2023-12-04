# ---------------------------------------------------------------------
# Fail action
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from .base import BaseAction, ActionError


class FailAction(BaseAction[None, None]):
    """
    Always success/
    """

    name = "fail"

    async def execute(self: "FailAction", req: None) -> None:
        msg = "Always failed."
        raise ActionError(msg)
