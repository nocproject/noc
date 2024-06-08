# ---------------------------------------------------------------------
# setenv action
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from .base import BaseAction


class SetEnvAction(BaseAction):
    """
    Set environment variable.
    """

    name = "setenv"

    async def execute(self: "SetEnvAction", *, name: str, value: str, **kwargs: str) -> str:
        self.logger.info("Setting environment `%s` to `%s`", name, value)
        self.env[name] = value
        return value
