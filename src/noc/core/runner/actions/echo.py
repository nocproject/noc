# ---------------------------------------------------------------------
# echo action
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from .base import BaseAction


class EchoAction(BaseAction):
    """
    Pass input to output.
    """

    name = "echo"

    async def execute(self: "EchoAction", *, x: str, **kwargs: str) -> str:
        return x
