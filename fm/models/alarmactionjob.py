# ---------------------------------------------------------------------
# Alarm Action Job model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import datetime
import logging
import enum
from typing import List, Set, Iterable, Optional, Tuple, Dict, Any

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BinaryField,
    DateTimeField,
    ListField,
    LongField,
    EnumField,
    IntField,
    EmbeddedDocumentListField,
    ObjectIdField,
    BooleanField,
    DictField,
)
from bson import ObjectId

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.span import get_current_span
from noc.core.fm.enum import RCA_DOWNLINK_MERGE
from noc.core.tt.types import (
    EscalationItem as ECtxItem,
    EscalationServiceItem,
    EscalationStatus,
    EscalationResult,
    EscalationMember,
    TTActionContext,
    TTAction,
    EscalationRequest,
)
from noc.core.tt.base import TTSystemCtx
from noc.core.scheduler.job import Job
from noc.aaa.models.user import User
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.servicesummary import SummaryItem, ObjectSummaryItem
from noc.sa.models.service import Service
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.utils import get_alarm

logger = logging.getLogger(__name__)


class ActionStatus(enum.Enum):
    """
    Job status.

    Attributes:
        * `p` - Pending, waiting for manual approve.
        * `w` - Waiting, ready to run.
        * `f` - Failed with error
        * `w` - Warning. Failed, but allowed to fail.
        * 'e' - End Wait
    """

    WAITING = "w"
    NEW = "n"
    SUCCESS = "s"
    FAILED = "f"
    WARNING = "W"
    CANCELLED = "c"
    SKIP = "s"
    WAIT_END = "we"


class JobStatus(enum.Enum):
    """
    Job status.

    Attributes:
        * `p` - Pending, waiting for manual approve.
        * `w` - Waiting, ready to run.
        * `r` - Running
        * `S` - Suspended
        * `s` - Success
        * `f` - Failed with error
        * `w` - Warning. Failed, but allowed to fail.
        * 'e' - End Wait
        * `c` - Cancelled
    """

    PENDING = "p"
    WAITING = "w"
    RUNNING = "r"
    SUSPENDED = "S"
    SUCCESS = "s"
    FAILED = "f"
    WARNING = "W"
    CANCELLED = "c"


class ItemStatus(enum.Enum):
    """
    Attributes:
        NEW: New items
        CHANGED: Items was changed
        FAIL: Failed when add to escalation
        EXISTS: Escalate over another doc
        REMOVED: Removed from escalation
    """

    NEW = "new"  # new item
    CHANGED = "changed"  # item changed
    FAIL = "fail"  # escalation fail
    EXISTS = "exists"  # Exists on another escalation
    REMOVED = "removed"  # item removed


class EscalationItem(EmbeddedDocument):
    """
    Escalation affected items. First item it escalation leader
    Attributes:
        managed_object_id: Alarm managed_object
        target_reference: Unique resource key
        alarm: Alarm Id item
        status: Item status
    """

    meta = {"strict": False}
    managed_object_id: int = IntField()
    target_reference = BinaryField(required=False)
    alarm = ObjectIdField()
    status = EnumField(ItemStatus, default=ItemStatus.NEW)
    # Already escalated doc

    def __str__(self) -> str:
        return f"{self.managed_object.name}:{self.alarm}"

    @property
    def managed_object(self) -> "ManagedObject":
        """"""
        return ManagedObject.get_by_id(self.managed_object_id)

    @property
    def is_new(self) -> bool:
        """Check if item is new (no escalation attempts)"""
        return self.status == ItemStatus.NEW

    @property
    def is_already_escalated(self) -> bool:
        """Check if item is already escalated"""
        return self.status == ItemStatus.EXISTS

    @property
    def is_maintenance(self) -> bool:
        """Check ManagedObject in Maintenance"""
        return self.managed_object.in_maintenance


class ActionLog(EmbeddedDocument):
    """
    Attributes:
        status: Action Status
        action: Action type
        user: User for action
        contact: Receiver address
        message: Notify/comment message
    """

    timestamp = DateTimeField()
    status: EscalationStatus = EnumField(EscalationStatus)
    # ack_alarm, close_alarm, add_comment ? User
    action: TTAction = EnumField(TTAction, required=True)
    # User Actions
    user: Optional["User"] = ForeignKeyField(User, required=False)
    contact: Optional[str] = StringField()
    message: Optional[str] = StringField()


class EscalationStep(EmbeddedDocument):
    """
    Escalation Log item
    Attributes:
        timestamp: Escalation Timestamp
        member: Escalation member
        key: Member Id
        document_id: Escalation ID on TTSystem
        retries: Escalation runs count
        status: Escalation Status
        error: Error when status is not ok
        end_status: End escalation status on TT System
        end_error: Error on deescalation process
    """

    meta = {"strict": False}

    # Action
    member = EnumField(EscalationMember, required=True)
    key: str = StringField(required=True)
    stop_processing = BooleanField(default=False)
    # Action Ctx
    acton_ctx = DictField(required=False)
    # template: Template = ForeignKeyField(Template)
    document_id = StringField()
    # end_template: Template = ForeignKeyField(Template, required=False)
    # Match
    delay: int = IntField(default=0)
    run_policy: str = StringField(
        choices=["start", "end", "both", "one", "manual"], default="both",
    )
    ack_policy: str = StringField(
        choices=[
            ("ack", "Alarm Acknowledge"),
            ("nack", "Alarm not Acknowledge"),
            # wait ack ?
            ("any", "Any Acknowledge"),
        ],
        default="any",
    )
    time_pattern = StringField(required=False)
    min_severity = IntField(default=0)
    # Status
    status: EscalationStatus = EnumField(EscalationStatus, default=EscalationStatus.NEW)
    error = StringField()
    # data = Dict
    # End Block
    end_status: EscalationStatus = EnumField(EscalationStatus)
    end_error = StringField()
    # results = DictField(required=False)
    # Job Source
    # user: Optional["User"] = ForeignKeyField(User, required=False)
    # tt_system: Optional["User"] = ForeignKeyField(User, required=False)

    def __str__(self):
        return ""

    def is_match(self, alarm, is_end: bool = False) -> bool:
        """Check match condition"""
        return True


class AlarmActionJob(Document):
    meta = {
        "collection": "alarm_action_jobs",
        "strict": False,
        "auto_create_index": False,
        "indexes": [ ],
    }

    status: JobStatus = EnumField(JobStatus, default=JobStatus.WAITING)
    items: List[EscalationItem] = EmbeddedDocumentListField(EscalationItem)
    created_at = DateTimeField(required=True)
    started_at = DateTimeField(required=False)
    completed_at = DateTimeField(required=False)
    ctx_id: int = LongField(required=False)  # Ctx
    # Policy
    end_condition = StringField(
        required=True,
        choices=[
            ("CR", "Close Root"),
            ("CA", "Close All"),
            ("E", "End Chain"),
            ("CT", "Close TT"),  # By Adapter
            ("M", "Manual"),  # By Adapter
        ],
        default="CR",
    )
    # Document options
    # is_dirty = BooleanField(default=True)  # Set if items was changed, Calculate by status
    # forced = BooleanField(default=False)
    telemetry_sample = IntField(default=0)
    actions: List[EscalationStep] = EmbeddedDocumentListField(EscalationStep)
    # Alarm Path ?
    groups = ListField(BinaryField())
    affected_services = ListField(ObjectIdField())
    # affected_maintenances = ListField(ObjectIdField())
    # Escalation summary
    severity: int = IntField(min_value=0)
    subject: Optional[str] = StringField(required=False)
    total_objects: List[ObjectSummaryItem] = EmbeddedDocumentListField(ObjectSummaryItem)
    total_services: List[SummaryItem] = EmbeddedDocumentListField(SummaryItem)
    total_subscribers: List[SummaryItem] = EmbeddedDocumentListField(SummaryItem)
    expires = DateTimeField(required=False)

    def __str__(self):
        return ""

    @property
    def is_end(self) -> bool:
        """Check EndCondition"""
        return False

    @property
    def leader(self) -> EscalationItem:
        """Escalation Leader - First"""
        # for ii in self.items:
        #    if ii.status == ItemStatus.REMOVED:
        #        continue
        #    return ii
        return self.items[0]

    @property
    def consequences(self) -> List[EscalationItem]:
        return self.items[1:]

    @property
    def alarm(self) -> Optional[ActiveAlarm]:
        return get_alarm(self.leader.alarm)

    @property
    def managed_object(self) -> Optional[ManagedObject]:
        for ii in self.items:
            if ii.status == ItemStatus.REMOVED:
                return ii.managed_object
        return self.leader.managed_object

    def from_request(self, req: EscalationRequest) -> "AlarmActionJob":
        """"""

    def from_alarm(self, alarm: ActiveAlarm) -> "AlarmActionJob":
        """"""

    def run(self):
        """Run Job"""
        logger.info("Performing escalations")
        changes = self.object.is_dirty
        if self.object.is_dirty:
            self.object.update_items()
            self.object.is_dirty = False
        # Check end escalation
        # if self.check_end():
        #     self.end_escalation()
        #     if not self.error:
        #         self.remove_job()
        #     return
        with (
            Span(
                client="escalator",
                sample=self.get_span_sample(),
                context=self.object.ctx_id,
            ),
            self.lock.acquire(self.object.get_lock_items()),
            change_tracker.bulk_changes(),
        ):
            if not self.object.ctx_id:
                # span_ctx.span_context
                self.object.set_escalation_context()
            ctx = self.object.get_ctx()
            for action in self.actions:
                if action.status != ActionStatus.WAITING or not action.is_match(self.alarm):
                    continue
                elif action.status == ActionStatus.WARNING:
                    ...
                    # Retry
                status, error, result = self.run_action(action.member, **action.acton_ctx)
                action.status = status
                action.error = error
                if result:
                    action.acton_ctx |= result


    def run_action(self, action: TTAction, key: str, **ctx: Dict[str, str]) -> Tuple[ActionStatus, str, Optional[Dict[str, str]]]:
        """Execute action"""

    def get_tt_system_context(
        self, tt_system: TTSystem, tt_id: Optional[str] = None
    ) -> TTSystemCtx:
        """
        Build TTSystem Context
        Args:
            tt_system: TTSystem instance
            tt_id: Document ID

        """
        cfg = self.get_tt_system_config(tt_system)
        actions = self.get_action_context()
        ctx = TTSystemCtx(
            id=tt_id,
            tt_system=tt_system.get_system(),
            queue=self.items[0].managed_object.tt_queue,
            reason=None,
            login=cfg.login,
            timestamp=self.started_at,
            actions=actions,
            items=self.get_escalation_items(tt_system) if cfg.promote_item else [],
            services=self.get_affected_services_items() or None,
            suppress_tt_trace=False,
        )
        return ctx


    def check_escalated(self, tt_system: TTSystem) -> bool:
        """Check item already escalated"""

    def create_tt(
        self,
        tt_system: TTSystem,
        subject: str,
        body: str,
        context: Optional[Dict[str, Any]] = None,
        tt_id: Optional[str] = None,
    ) -> EscalationResult:
        """
        Create Trouble Ticket on TT System

        Args:
            tt_system: TT System instance
            subject: Message Subject
            body: Message Body
            context: Escalation Context
            tt_id: If set, do changes

        Returns:
            EscalationResult:
        """
        logger.debug(
            "[%s] Escalation message:\nSubject: %s\n%s",
            self.id,
            subject,
            body,
        )