# ---------------------------------------------------------------------
# Dump action
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from .base import BaseAction


class DumpAction(BaseAction):
    """
    Dump environment.
    """

    name = "dump"

    async def execute(self: "DumpAction", **kwargs: str) -> None:
        self.logger.info("Dumping environment")
        for k, v in sorted(self.env.items()):
            self.logger.info("%s = %s", k, v)
