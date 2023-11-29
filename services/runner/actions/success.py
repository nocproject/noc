# ---------------------------------------------------------------------
# Success action
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from .base import BaseAction


class SuccessAction(BaseAction[None, None]):
    """
    Always success.
    """

    name = "success"

    async def execute(self: "SuccessAction", req: None) -> None:
        pass
