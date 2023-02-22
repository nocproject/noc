# ----------------------------------------------------------------------
# Base TT System
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Optional, List

# NOC modules
from .types import DeescalationContext, EscalationContext, TTInfo, TTCommentRequest
from .error import TTError, TemporaryTTError


class BaseTTSystem(object):
    """
    Base class for TT integration adapter.

    Args:
        name: TT system name
        connection: Connection settings string, as defined
            in TTSystem.connection

    Attributes:
        TTError: Basic error.
        TemporaryTTError: Transient error, escalation
            can be restarted.
    """

    TTError = TTError
    TemporaryTTError = TemporaryTTError

    def __init__(self, name: str, connection: str):
        self.connection = connection
        self.name = name
        self.logger = logging.getLogger("tt.%s" % self.name)

    def create(self, ctx: EscalationContext) -> str:
        """
        Create TT.

        Override to implement custom logic.

        Args:
            ctx: EscalationContext structure.

        Returns:
            Created TT id.

        Raises:
            TemporaryTTError: When escalation attempt may be retried.
            TTError: When escalation is failed.
        """
        return self.create_tt(ctx)

    def close(self, ctx: DeescalationContext) -> None:
        """
        Close TT.

        Args:
            ctx: Deescalation context.

        Raises:
            TTError: on deescalation error.
        """

        self.close_tt(ctx)

    def create_tt(self, ctx: EscalationContext) -> str:
        """
        Create TT implemetation.

        Args:
            ctx: EscalationContext structure.

        Returns:
            Created TT id

        Raises:
            TemporaryTTError: When escalation attempt may be retried.
            TTError: When escalation is failed.
        """
        raise NotImplementedError()

    def get_tt(self, tt_id: str) -> Optional[TTInfo]:
        """
        Get TT information.

        Args:
            tt_id: TT id, as returned by create_tt.

        Returns:
            Optional TTInfo structure

        Raise:
            TTError: On TT system error.
        """
        raise NotImplementedError()

    def get_object_tts(self, obj: str) -> List[str]:
        """
        Get list of TTs, open for object obj
        :param obj: Supported object id, as passed to create_tt
        :raises TTError:
        """
        raise NotImplementedError()

    def close_tt(self, ctx: DeescalationContext) -> None:
        """
        Close TT implementation.

        Args:
            ctx: Deescalation context.

        Raises:
            TTError: on deescalation error.
        """
        raise NotImplementedError()

    def comment(self, req: TTCommentRequest) -> None:
        """
        Add comment to TT.

        Args:
            req: TTCommentRequest

        Raises:
            TTError: On comment error.
        """
        raise NotImplementedError()
