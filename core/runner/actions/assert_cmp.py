# ---------------------------------------------------------------------
# assert_cmp action
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Callable, Dict

# NOC modules
from .base import BaseAction, ActionError


class AssertCmpAction(BaseAction):
    """
    Ensure input comparison is True.

    Apply `op` to compare `x` and `y`.
    Raise error if operation is failed
    """

    name = "assert_cmp"

    _OPS: Dict[str, Callable[[str, str], bool]] = {
        "==": lambda x, y: x == y,
        "!=": lambda x, y: x != y,
        "<": lambda x, y: x < y,
        "<=": lambda x, y: x <= y,
        ">": lambda x, y: x > y,
        ">=": lambda x, y: x >= y,
    }

    async def execute(self: "AssertCmpAction", *, op: str, x: str, y: str, **kwargs: str) -> None:
        if not self._OPS[op](x, y):
            self.logger.error("Failed to compare '%s' %s '%s'", x, op, y)
            msg = "Failed to compare"
            raise ActionError(msg)
