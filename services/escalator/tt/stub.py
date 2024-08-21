# ----------------------------------------------------------------------
#  Stub TT System
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import uuid
import logging

# NOC modules
from noc.core.tt.base import BaseTTSystem
from noc.core.tt.types import (
    EscalationContext,
    DeescalationContext,
)
from noc.core.span import Span


class StubTTSystem(BaseTTSystem):
    """
    Stub TT system responds as a valid one, generating unique TT ids.
    For debugging purposes only
    """

    promote_group_tt = True

    def __init__(self, name, connection):
        super().__init__(name, connection)
        self.logger = logging.getLogger("StubTTSystem.%s" % name)

    def create(self, ctx: EscalationContext) -> str:
        with Span(server="telegram", service="sendMessage"):
            self.logger.info(
                "create_tt(queue=%s, obj=%s, reason=%s, subject=%s, body=%s, login=%s, timestamp=%s)",
                ctx.queue,
                ctx.leader,
                ctx.reason,
                ctx.subject,
                ctx.body,
                ctx.login,
                ctx.timestamp,
            )
            return str(uuid.uuid4())

    def add_comment(self, tt_id, subject=None, body=None, login=None, queue=None):
        self.logger.info(
            "add_comment(tt_id=%s, subject=%s, body=%s, login=%s)", tt_id, subject, body, login
        )
        return True

    def close(self, ctx: DeescalationContext) -> None:
        """
        Close TT.

        Args:
            ctx: Deescalation context.

        Raises:
            TTError: on deescalation error.
        """
        with Span(server="telegram", service="deleteMessage", in_label=ctx.id):
            self.logger.info("TT %s closed", ctx.tt_id)
