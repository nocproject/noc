# ----------------------------------------------------------------------
# Base TT System
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from datetime import datetime
from typing import Optional, List

# NOC modules
from .types import (
    DeescalationContext,
    EscalationContext,
    TTActionContext,
    TTInfo,
    TTCommentRequest,
    EscalationItem,
    EscalationServiceItem,
    EscalationStatus,
    EscalationResult,
    TTChange,
    TTAction,
)
from .error import TTError, TemporaryTTError
from noc.core.debug import error_report


class BaseTTSystem(object):
    """
    Base class for TT integration adapter.

    Args:
        name: TT system name
        connection: Connection settings string, as defined
            in TTSystem.connection

    Attributes:
        promote_group_tt: Supported Group Alarm
        processed_items: Supported processed alarm items
        actions: List of available actions, for TTSystem
        TTError: Basic error.
        TemporaryTTError: Transient error, escalation
            can be restarted.
    """

    TTError = TTError
    TemporaryTTError = TemporaryTTError
    promote_group_tt = True
    processed_items = False
    actions: List[TTAction] = []

    def __init__(self, name: str, connection: str):
        self.connection = connection
        self.name = name
        self.logger = logging.getLogger(f"tt.{self.name}")

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
        Create TT implementation.

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

        Args:
            obj: Supported object id, as passed to create_tt

        Raise:
            TTError: On TT system error.
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

    def get_updates(
        self,
        last_run: Optional[datetime] = None,
        last_update: Optional[str] = None,
        tt_ids: Optional[List[str]] = None,
    ) -> List[TTChange]:
        """
        Getting updates from TT system

        Args:
            last_run: timestamp last run
            last_update: Last update sequence number
            tt_ids: List document id for request changes

        """
        raise NotImplementedError()


class TTSystemCtx(object):
    """
    Escalation context data class.

    This structure is passed to TTSystem
    during the escalation process.

    Attributes:
        queue: TT system's queue to place TT
        login: TT system's login
        timestamp: Alarm timestamp.
        id: Document id
        actions: Available action Context
        items: Managed object references. Leader is first.
    """

    def __init__(
        self,
        tt_system: BaseTTSystem,
        timestamp=None,
        id=None,
        queue=None,
        reason=None,
        login=None,
        actions=None,
        items=None,
        services=None,
        suppress_tt_trace: bool = True,
        is_unavailable: bool = False,
    ):
        self.tt_system: BaseTTSystem = tt_system
        self.id: Optional[str] = id
        self.timestamp: Optional[datetime] = timestamp
        self.queue: Optional[str] = queue
        self.reason: Optional[str] = reason
        self.login: Optional[str] = login
        self.items: List[EscalationItem] = items or []
        self.services: List[EscalationServiceItem] = services or []
        self.actions: List[TTActionContext] = actions or []
        self.error_code: Optional[str] = None
        self.error_text: Optional[str] = ""
        self.suppress_tt_trace: bool = suppress_tt_trace
        self.is_unavailable = is_unavailable

    def get_result(self) -> EscalationResult:
        if self.error_code:
            return EscalationResult(
                status=EscalationStatus(self.error_code),
                error=self.error_text,
                document=self.id,
            )
        return EscalationResult(document=self.id)

    @property
    def leader(self) -> EscalationItem:
        """
        Escalation leader.
        """
        return self.items[0]

    def add_items(self, items: List[EscalationItem]):
        self.items += items

    def get_config(self):
        """

        :return:
        """

    def create(
        self,
        subject: str,
        body: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create Document on TT System

        Args:
            subject: Document subject
            body: Document Body
            severity: Document Data

        """
        self.id = self.tt_system.create(
            EscalationContext(
                id=self.id,
                queue=self.queue,
                services=self.services,
                reason=self.reason,
                login=self.login,
                timestamp=self.timestamp,
                subject=subject,
                body=body,
                actions=self.actions,
                items=self.items,
                is_unavailable=self.is_unavailable,
            )
        )
        return self.id

    def comment_tt(self, message: str):
        """
        Add document commentaries
        :return:
        """
        """Append comment to tt"""
        self.tt_system.comment(
            TTCommentRequest(
                id=self.id,
                subject=message,
                body=None,
                login=self.login,
                queue=self.queue,
            )
        )

    def close(self, subject: Optional[str] = None, body: Optional[str] = None):
        """
        Close document in TT System
        :return:
        """
        self.tt_system.close(
            DeescalationContext(
                id=self.id,
                subject=subject,
                body=body,
                login=self.login,
                queue=self.queue,
            )
        )

    def get_updates(
        self, last_run: Optional[datetime] = None, last_number: Optional[str] = None
    ) -> List[TTChange]:
        """
        Getting updates from TT system

        Args:
            last_run: date before getting update
            last_number:
        """
        raise NotImplementedError()

    def __enter__(self):
        if not isinstance(self.tt_system, BaseTTSystem):
            raise AttributeError("tt_system must be BaseTTSystem instance")
        if not self.tt_system:
            return
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is TemporaryTTError:
            # "temp"
            self.set_error("temp", str(exc_val))
        elif exc_type is TTError:
            # "fail"
            self.set_error("fail", str(exc_val))
        elif exc_type is NotImplementedError:
            self.set_error("skip", str(exc_val))
        elif exc_type:
            self.set_error("fail", str(exc_val))
            if not self.suppress_tt_trace:
                error_report()
        return True

    def set_error(self, code: Optional[str] = None, text: Optional[str] = None) -> None:
        """
        Set error result and code for current span
        :param code: Optional error code
        :param text: Optional error text
        :return:
        """
        if code is not None:
            self.error_code = code
        if text is not None:
            self.error_text = text
