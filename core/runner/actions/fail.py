# ---------------------------------------------------------------------
# Fail action
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from .base import BaseAction, ActionError


class FailAction(BaseAction):
    """
    Always success/
    """

    name = "fail"

    async def execute(self: "FailAction", **kwargs: str) -> None:
        msg = "Always failed."
        raise ActionError(msg)
