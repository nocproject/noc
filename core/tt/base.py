# ----------------------------------------------------------------------
# Base TT System
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Optional, List

# NOC modules
from .types import EscalationContext, TTInfo
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

    def close_tt(self, tt_id, subject=None, body=None, reason=None, login=None, queue=None):
        """
        Close TT
        :param tt_id: TT id, as returned by create_tt
        :param subject: Closing message subject
        :param body: Closing message body
        :param reason: Final reason
        :param login: User login
        :param queue: ticket queue
        :returns: Boolean. True, when alarm is closed properly
        :raises TTError:
        """
        raise NotImplementedError()

    def add_comment(self, tt_id, subject=None, body=None, login=None, queue=None):
        """
        Append comment to TT
        :param tt_id: TT id, as returned by create_tt
        :param subject: Closing message subject
        :param body: Closing message body
        :param login: User login
        :param queue: ticket queue
        :raises TTError:
        """
        raise NotImplementedError()
