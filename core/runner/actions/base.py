# ---------------------------------------------------------------------
# Action Base Class
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import TypeVar, Dict, Union, Optional
from logging import Logger
from inspect import signature

# NOC modules
from noc.core.error import NOCError
from ..env import Environment

REQ = TypeVar("REQ")
RESP = TypeVar("RESP")


class ActionError(NOCError):
    pass


class ActionMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        m = type.__new__(mcs, name, bases, attrs)
        # Get inputs
        m.inputs = {}
        sig = signature(m.execute)
        for param in sig.parameters.values():
            if param.kind != param.KEYWORD_ONLY:
                continue
            m.inputs[param.name] = param.annotation == Optional[str]
        return m


class BaseAction(object, metaclass=ActionMetaclass):
    """
    Base class for actions.

    Subclasses must override `execute` method.

    Args:
        env: Environment instance.
    """

    name: str
    inputs: Dict[str, bool]  # Set by metaclass

    def __init__(self, env: Environment, logger: Logger):
        self.env = env
        self.logger = logger

    async def execute(self, **kwargs: str) -> Union[None, str, object]:
        """
        Process request and generate response.

        Returns:
            response.
        Raises:
            ActionError
        """
        raise NotImplementedError()
