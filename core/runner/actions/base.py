# ---------------------------------------------------------------------
# Action Base Class
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Generic, TypeVar, Dict
from logging import Logger

# NOC modules
from noc.core.error import NOCError

REQ = TypeVar("REQ")
RESP = TypeVar("RESP")


class ActionError(NOCError):
    pass


class BaseAction(Generic[REQ, RESP]):
    """
    Base class for actions.

    Subclasses must override `handle` method.

    Args:
        env: Environment instance.
    """

    name: str

    def __init__(self, env: Dict[str, str], logger: Logger):
        self.env = env
        self.logger = logger

    async def execute(self, req: REQ) -> RESP:
        """
        Process request and generate response.

        Args:
            req: Request type.
        Returns:
            response.
        Raises:
            ActionError
        """
        raise NotImplementedError()
