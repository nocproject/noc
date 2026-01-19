# ---------------------------------------------------------------------
# ActiveAlarm model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging
import asyncio
import operator
from collections import defaultdict
from itertools import chain
from typing import (
    Optional,
    Set,
    Any,
    Dict,
    Iterable,
    Protocol,
    runtime_checkable,
    Generic,
    Union,
    List,
)

# Third-party modules
import orjson
from bson import ObjectId
from jinja2 import Template as Jinja2Template
from pymongo import UpdateOne
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    DateTimeField,
    ListField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    IntField,
    LongField,
    ObjectIdField,
    DictField,
    BinaryField,
    EnumField,
)
from mongoengine.errors import SaveConditionError

# NOC modules
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.models import get_model
from noc.aaa.models.user import User
from noc.main.models.style import Style
from noc.main.models.template import Template
from noc.main.models.label import Label
from noc.main.models.remotesystem import RemoteSystem
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.servicesummary import ServiceSummary, SummaryItem, ObjectSummaryItem
from noc.core.change.decorator import change
from noc.core.defer import call_later
from noc.core.defer import defer
from noc.core.debug import error_report
from noc.config import config
from noc.core.span import get_current_span
from noc.core.fm.enum import RCA_NONE, RCA_OTHER, RCA_DOWNLINK_MERGE, GroupType
from noc.core.handler import get_handler
from .alarmseverity import AlarmSeverity
from .alarmclass import AlarmClass
from .alarmlog import AlarmLog
from .ttsystem import TTSystem, DEFAULT_TTSYSTEM_SHARD
from .alarmwatch import Effect, WatchItem


@change(audit=False)
class ActiveAlarm(Document):
    meta = {
        "collection": "noc.alarms.active",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "timestamp",
            "root",
            "-severity",
            "wait_ts",
            ("alarm_class", "managed_object"),
            "#reference",
            ("timestamp", "managed_object"),
            "log.tt_id",
            # "escalation_ts",
            "adm_path",
            "segment_path",
            "container_path",
            "uplinks",
            ("alarm_class", "rca_neighbors"),
            "labels",
            "effective_labels",
            "groups",
            ("root", "groups"),
            ("root", "rca_type"),
            "deferred_groups",
        ],
    }
    status = "A"

    timestamp = DateTimeField(required=True)
    last_update = DateTimeField(required=True)
    managed_object: "ManagedObject" = ForeignKeyField(ManagedObject)
    alarm_class: "AlarmClass" = PlainReferenceField(AlarmClass)
    # Calculated Severity
    severity = IntField(required=True)
    base_severity = IntField(required=False)
    vars = DictField()
    # Alarm reference is a hash of discriminator
    # for external systems
    reference = BinaryField(required=False)
    log: List[AlarmLog] = EmbeddedDocumentListField(AlarmLog)
    # Manual acknowledgement timestamp
    ack_ts = DateTimeField(required=False)
    # Manual acknowledgement user name
    ack_user = StringField(required=False)
    opening_event = ObjectIdField(required=False)
    closing_event = ObjectIdField(required=False)
    # List of subscribers
    watchers: List[WatchItem] = EmbeddedDocumentListField(WatchItem)
    custom_subject = StringField(required=False)
    custom_object = StringField(required=False)
    custom_style = ForeignKeyField(Style, required=False)
    reopens = IntField(required=False)
    # RCA
    # Reference to root cause (Active Alarm or Archived Alarm instance)
    root = ObjectIdField(required=False)
    # Group alarm references
    groups = ListField(BinaryField())
    # Minimal group size
    min_group_size = IntField(min_value=0)
    # Groups waiting to min_threshold quorum
    deferred_groups = ListField(BinaryField())
    # span context
    escalation_ctx = LongField(required=False)
    wait_ts: Optional[datetime.datetime] = DateTimeField(required=False)
    # Directly affected services summary, grouped by profiles
    # (connected to the same managed object)
    direct_objects = ListField(EmbeddedDocumentField(ObjectSummaryItem))
    direct_services = ListField(EmbeddedDocumentField(SummaryItem))
    direct_subscribers = ListField(EmbeddedDocumentField(SummaryItem))
    # Indirectly affected services summary, grouped by profiles
    # (covered by this and all inferred alarms)
    total_objects = ListField(EmbeddedDocumentField(ObjectSummaryItem))
    total_services = ListField(EmbeddedDocumentField(SummaryItem))
    total_subscribers = ListField(EmbeddedDocumentField(SummaryItem))
    # Paths
    adm_path = ListField(IntField())
    segment_path = ListField(ObjectIdField())
    container_path = ListField(ObjectIdField())
    # Services
    affected_services = ListField(ObjectIdField())
    # Uplinks, for topology_rca only
    uplinks = ListField(IntField())
    # RCA neighbor cache, for topology_rca only
    rca_neighbors = ListField(IntField())
    dlm_windows = ListField(IntField())
    # RCA_* enums
    rca_type = IntField(default=RCA_NONE)
    group_type: GroupType = EnumField(GroupType, default=GroupType.NEVER)
    # labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem, required=False)
    # Object id in remote system
    remote_id = StringField(required=False)

    def __str__(self):
        return str(self.id)

    @classmethod
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ActiveAlarm"]:
        return ActiveAlarm.objects.filter(id=oid).first()

    @classmethod
    def get_by_tt_id(cls, tt_id: str) -> Optional["ActiveAlarm"]:
        return ActiveAlarm.objects.filter(log__tt_id=tt_id).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_alarm:
            yield "alarm", str(self.id)

    def get_escalation_log(self, tt_system: TTSystem) -> Optional[AlarmLog]:
        for ll in self.log:
            if ll.tt_id and ll.tt_id.startswith(f"{tt_system.name}:"):
                return ll

    @property
    def escalation_tt(self) -> Optional[str]:
        for ll in self.log:
            if ll.tt_id:
                return ll.tt_id

    @property
    def escalation_ts(self) -> Optional[datetime.datetime]:
        for ll in self.log:
            if ll.tt_id:
                return ll.timestamp

    @property
    def escalation_error(self) -> Optional[str]:
        from noc.fm.models.escalation import Escalation

        esc = Escalation.objects.filter(items__alarm=self.id, close_timestamp__exists=False).first()
        if not esc:
            return None
        for ii in esc.items:
            if ii.escalation_status in ("fail", "temp"):
                return ii.escalation_error

    @property
    def escalator_shard(self):
        if self.managed_object:
            return self.managed_object.escalator_shard
        return DEFAULT_TTSYSTEM_SHARD

    @property
    def severity_policy(self) -> Optional[str]:
        """Getting severity policy for alarm"""
        if self.alarm_class.affected_service:
            policy = "AB"
        else:
            policy = None
        for w in self.watchers:
            if w.effect == Effect.SEVERITY:
                policy = w.args.get("policy")
        return policy

    @property
    def clear_timestamp(self) -> Optional[datetime.datetime]:
        """Return clear timestamp for Template Compat"""
        if hasattr(self, "_clear_ts"):
            return self._clear_ts
        return None

    @classmethod
    def get_min_wait_ts(cls) -> Optional[datetime.datetime]:
        """"""
        return (
            ActiveAlarm.objects()
            .aggregate(
                [
                    {"$group": {"_id": None, "min_wait_ts": {"$min": "$wait_ts"}}},
                ]
            )
            .next()["min_wait_ts"]
        )

    def clean(self):
        super().clean()
        if not self.last_update:
            self.last_update = self.timestamp
        if self.managed_object:
            self.adm_path = self.managed_object.adm_path
            self.segment_path = self.managed_object.segment_path
            self.container_path = self.managed_object.container_path
            self.uplinks = self.managed_object.uplinks
            self.rca_neighbors = self.managed_object.rca_neighbors
            self.dlm_windows = self.managed_object.dlm_windows
        else:
            self.adm_path = []
            self.segment_path = []
            self.container_path = []
            self.uplinks = []
            self.rca_neighbors = []
            self.dlm_windows = []
        self.reopens = self.reopens or 0
        if not self.id:
            # Update effective labels
            self.effective_labels = list(chain.from_iterable(self.iter_effective_labels(self)))

    def safe_save(self, **kwargs):
        """
        Create new alarm or update existing if still exists
        """
        if self.id:
            # Update existing only if exists
            if "save_condition" not in kwargs:
                kwargs["save_condition"] = {"id": self.id}
            try:
                self.last_update = datetime.datetime.now().replace(microsecond=0)
                self.save(**kwargs)
            except SaveConditionError:
                pass  # Race condition, closed during update
        else:
            self.save()

    def change_severity(
        self,
        user="",
        delta=None,
        severity: Optional[Union[int, AlarmSeverity]] = None,
        to_save=True,
    ):
        """
        Change alarm severity
        """
        if isinstance(user, User):
            user = user.username
        if delta:
            self.severity = max(0, self.severity + delta)
            if delta > 0:
                self.log_message(f"{user} has increased alarm severity by {delta}")
            else:
                self.log_message(f"{user} has decreased alarm severity by {delta}")
        elif severity:
            if isinstance(severity, (float, int)):
                self.severity = int(severity)
                self.log_message(f"{user} has changed severity to {severity}")
            else:
                self.severity = severity.severity
                self.log_message(f"{user} has changed severity to {severity.name}")
        if to_save:
            self.safe_save()

    def log_message(
        self,
        message,
        to_save=True,
        bulk: Optional[List[Any]] = None,
        source: Optional[str] = None,
        tt_id: Optional[str] = None,
    ):
        if bulk is not None:
            bulk += [
                UpdateOne(
                    {"_id": self.id},
                    {
                        "$push": {
                            "log": {
                                "timestamp": datetime.datetime.now(),
                                "from_status": self.status,
                                "to_status": self.status,
                                "message": message,
                                "source": source,
                                "tt_id": tt_id,
                            }
                        }
                    },
                )
            ]
        self.log += [
            AlarmLog(
                timestamp=datetime.datetime.now(),
                from_status=self.status,
                to_status=self.status,
                message=message,
                source=source,
                tt_id=tt_id,
            )
        ]
        if to_save and not bulk:
            self.safe_save()

    @property
    def allow_clear(self) -> bool:
        """Check Alarm allowed for clear"""
        return all(w.effect != Effect.STOP_CLEAR for w in self.watchers or [])

    def clear_alarm(
        self,
        message,
        ts: Optional[datetime.datetime] = None,
        force: bool = False,
        source=None,
        dry_run: bool = False,
    ) -> Optional["ArchivedAlarm"]:
        """
        Clear alarm
        Args:
            message: Log clearing message
            ts: Clearing timestamp
            force: Clear ever if wait_tt seg
            source: Source clear alarm
            dry_run: Do not call save()
        """
        from .alarmdiagnosticconfig import AlarmDiagnosticConfig

        if self.alarm_class.is_ephemeral:
            self.delete()
        ts = ts or datetime.datetime.now()
        if not force and not self.allow_clear:
            self.add_watch(Effect.CLEAR_ALARM, key="", immediate=True)
            return None
        if self.alarm_class.clear_handlers:
            # Process clear handlers
            for h in self.alarm_class.get_clear_handlers():
                try:
                    h(self)
                except Exception:
                    error_report()
        log = [
            *self.log,
            AlarmLog(timestamp=ts, from_status="A", to_status="C", message=message, source=source),
        ]
        a = ArchivedAlarm(
            id=self.id,
            timestamp=self.timestamp,
            clear_timestamp=ts,
            managed_object=self.managed_object,
            alarm_class=self.alarm_class,
            severity=self.severity,
            vars=self.vars,
            log=log,
            ack_ts=self.ack_ts,
            ack_user=self.ack_user,
            root=self.root,
            groups=self.groups,
            # Escalation_tts - list
            escalation_ts=self.escalation_ts,
            escalation_tt=self.escalation_tt,
            escalation_ctx=self.escalation_ctx,
            opening_event=self.opening_event,
            closing_event=self.closing_event,
            reference=self.reference,
            reopens=self.reopens,
            direct_objects=self.direct_objects,
            direct_services=self.direct_services,
            direct_subscribers=self.direct_subscribers,
            total_objects=self.total_objects,
            total_services=self.total_services,
            total_subscribers=self.total_subscribers,
            adm_path=self.adm_path,
            segment_path=self.segment_path,
            container_path=self.container_path,
            uplinks=self.uplinks,
            rca_neighbors=self.rca_neighbors,
            rca_type=self.rca_type,
            labels=self.labels,
            effective_labels=self.effective_labels,
            remote_system=self.remote_system,
            remote_id=self.remote_id,
        )
        self._clear_ts = ts
        ct = self.alarm_class.get_control_time(self.reopens)
        if ct:
            a.control_time = datetime.datetime.now() + datetime.timedelta(seconds=ct)
        if dry_run:
            self.status = "C"
            return a
        a.save()
        # Set checks on all consequences
        for d in self._get_collection().find(
            {"root": self.id}, {"_id": 1, "alarm_class": 1, "managed_object": 1}
        ):
            ac = AlarmClass.get_by_id(d["alarm_class"])
            if not ac:
                continue
            t = ac.recover_time
            if not t:
                continue
            call_later(
                "noc.services.correlator.check.check_close_consequence",
                scheduler="correlator",
                max_runs=3,
                pool=self.managed_object.get_effective_fm_pool().name,
                delay=t,
                shard=d.get("managed_object"),
                alarm_id=d["_id"],
            )
        # Clear alarm
        self.delete()
        if self.affected_services:
            defer(
                "noc.sa.models.service.refresh_service_status",
                svc_ids=[str(x) for x in self.affected_services],
            )
        # Close TT
        # MUST be after .delete() to prevent race conditions
        self.touch_watch(is_clear=True)
        # Gather diagnostics
        AlarmDiagnosticConfig.on_clear(a)
        # Return archived
        return a

    def get_template_vars(self) -> Dict[str, Any]:
        """
        Prepare template variables
        """
        r = self.vars.copy()
        r["alarm"] = self
        if self.managed_object:
            r["managed_object"] = self.managed_object
        return r

    @property
    def subject(self) -> str:
        if self.custom_subject:
            s = self.custom_subject
        else:
            s = Jinja2Template(self.alarm_class.subject_template).render(self.get_template_vars())
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s

    @property
    def body(self) -> str:
        # Replace to message context
        return Jinja2Template(self.alarm_class.body_template).render(self.get_template_vars())

    def get_message_body(
        self,
        template: Optional[Template] = None,
        subject_tag: Optional[str] = None,
        is_clear: bool = False,
    ):
        """
        Render alarm message body and subject
        Args:
            template: Custom template for message
            subject_tag: Custom subject tag for message
            is_clear: For clear_alarm message
        """
        r = {}
        if template:
            try:
                r = {
                    "subject": template.render_subject(
                        alarm=self, managed_object=self.managed_object
                    ),
                    "body": template.render_body(alarm=self, managed_object=self.managed_object),
                }
            except Exception as e:
                print(f"Error when render template: {e}")
        if not r and is_clear:
            r = {"subject": f"[Alarm Cleared] {self.subject}", "body": "Alarm has been cleared"}
        elif not r:
            r = {"subject": self.subject, "body": self.body}
        if subject_tag:
            r["subject"] = f"[{subject_tag}] {r['subject']}"
        return r

    @property
    def components(self) -> "ComponentHub":
        components = getattr(self, "_components", None)
        if components:
            return components
        self._components = ComponentHub(self.alarm_class, self.managed_object, self.vars)
        return self._components

    def subscribe(self, user: "User"):
        """
        Change alarm's subscribers
        """
        self.add_watch(Effect.SUBSCRIPTION, str(user.id))
        self.log_message(
            f"{user.get_full_name()}({user.username}): has been subscribed",
            to_save=False,
            source=user.username,
        )
        self.save()

    def unsubscribe(self, user: "User"):
        """Remove alarm subscription for user"""
        self.stop_watch(Effect.SUBSCRIPTION, str(user.id))
        self.log_message(
            f"{user.get_full_name()}({user.username}): has been unsubscribed",
            to_save=False,
            source=user.username,
        )
        self.save()

    def is_subscribed(self, user: "User") -> bool:
        return any(w.effect == Effect.SUBSCRIPTION and str(user.id) == w.key for w in self.watchers)

    @property
    def is_link_alarm(self) -> bool:
        return hasattr(self.components, "interface")

    def acknowledge(self, user: "User", msg=""):
        """Acknowledge alarm by user"""
        self.ack_ts = datetime.datetime.now()
        self.ack_user = user.username
        self.log = [
            *self.log,
            AlarmLog(
                timestamp=self.ack_ts,
                from_status="A",
                to_status="A",
                message="Acknowledged by %s(%s): %s" % (user.get_full_name(), user.username, msg),
                source=user.username,
            ),
        ]
        self.safe_save()
        self.touch_watch()

    def unacknowledge(self, user: "User", msg=""):
        """Delete acknowledge alarm by user"""
        self.ack_ts = None
        self.ack_user = None
        self.log = [
            *self.log,
            AlarmLog(
                timestamp=datetime.datetime.now(),
                from_status="A",
                to_status="A",
                message="Unacknowledged by %s(%s): %s" % (user.get_full_name(), user.username, msg),
                source=user.username,
            ),
        ]
        self.safe_save()
        self.touch_watch()

    def register_clear(
        self, msg: str, user: Optional[User] = None, timestamp: Optional[datetime.datetime] = None
    ):
        """
        Register Alarm Clear Request on Correlator
        Send clear signal to the correlator
        Args:
            msg: Clear reason text
            user: Set for Manual Clear
            timestamp: Clear Timestamp
        """
        from noc.core.service.loader import get_service
        from noc.main.models.pool import Pool

        if self.managed_object:
            fm_pool = self.managed_object.get_effective_fm_pool()
            partition = int(self.managed_object.id)
        else:
            fm_pool = Pool.get_default_fm_pool()
            partition = 0
        stream = f"dispose.{fm_pool.name}"
        service = get_service()
        num_partitions = asyncio.run(service.get_stream_partitions(stream))
        service.publish(
            orjson.dumps(
                {
                    "$op": "clearid",
                    "id": str(self.id),
                    "message": msg,
                    "source": user.username if user else "",
                    "timestamp": timestamp.isoformat() if timestamp else None,
                }
            ),
            stream=stream,
            partition=partition % num_partitions,
        )

    def get_wait_ts(self, timestamp: Optional[datetime.datetime] = None):
        wait_ts = []
        for w in self.watchers:
            if w.after:
                wait_ts.append(w.after)
        if timestamp:
            wait_ts.append(timestamp)
        if wait_ts:
            return min(wait_ts)
        return None

    def add_watch(
        self,
        effect: Effect,
        key: str,
        once: bool = False,
        immediate: bool = False,
        clear_only: bool = False,
        after: Optional[datetime.datetime] = None,
        keep_args: bool = False,
        **kwargs,
    ):
        """
        Adding watch
        Args:
            effect: Watched effect
            key: Effect key
            once: Run only once
            immediate: Already executed (used for save data/reference on external job)
            clear_only: Run only alarm clear
            after: Run After Timer
            keep_args: Keep arguments for exist effect
        """
        if effect == Effect.CLEAR_ALARM and (clear_only or once):
            raise ValueError("Not supported options")
        for w in self.watchers:
            if effect == w.effect and key == w.key:
                if not keep_args:
                    w.after = after
                    w.args = kwargs
                break
        else:
            self.watchers.append(
                WatchItem(
                    effect=effect,
                    key=str(key),
                    once=once,
                    immediate=immediate,
                    clear_only=clear_only,
                    after=after,
                    args=kwargs,  # Convert to string
                )
            )
        if after or self.wait_ts:
            self.wait_ts = self.get_wait_ts()

    def stop_watch(self, effect: Effect, key: str):
        """Stop waiting callback"""
        r = []
        for w in self.watchers:
            if w.effect == effect and w.key == key:
                continue
            r.append(w)
        if len(r) != len(self.watchers):
            self.watchers = r
            self.wait_ts = self.get_wait_ts()

    def touch_watch(
        self,
        is_clear: bool = False,
        is_update: bool = False,
        dry_run: bool = False,
    ):
        """
        Processed watchers
        Args:
            is_clear: Flag for alarm_clear procedure
            is_update: Flag for refresh_alarm procedure
            dry_run: For tests run
        """
        now = datetime.datetime.now() + datetime.timedelta(seconds=10)  # time drift
        for w in self.watchers:
            if w.clear_only and not is_clear:
                # Watch alarm_clear
                continue
            if w.once and is_update:
                continue
            if w.immediate:
                # If Immediate, not run (used for save run only)
                continue
            if w.after and w.after > now:
                continue
            try:
                w.run(self, is_clear=is_clear, dry_run=dry_run)
            except Exception as e:
                print(f"Exception when run Watch Action: {e}")

    @property
    def duration(self) -> int:
        dt = datetime.datetime.now() - self.timestamp
        return dt.days * 86400 + dt.seconds

    @property
    def display_duration(self) -> str:
        duration = datetime.datetime.now() - self.timestamp
        secs = duration.seconds % 60
        mins = (duration.seconds / 60) % 60
        hours = (duration.seconds / 3600) % 24
        days = duration.days
        r = "%02d:%02d:%02d" % (hours, mins, secs)
        if days:
            r = "%dd %s" % (days, r)
        return r

    @property
    def effective_style(self) -> "Style":
        if self.custom_style:
            return self.custom_style
        return AlarmSeverity.get_severity(self.severity).style

    def rewrite_alarm_class(self, alarm_class: "AlarmClass", dry_run: bool = False):
        """Replace Alarm Class on Active Alarm"""
        if alarm_class == self.alarm_class:
            return
        if self.alarm_class.allow_rewrite(alarm_class):
            return
        self.alarm_class = alarm_class
        if not dry_run:
            ActiveAlarm.objects.filter(id=self.id).update(alarm_class=self.alarm_class)

    def refresh_alarm_class(self, dry_run: bool = False):
        """Check current alarm class is actual, and update it"""
        # Calculate Effective AlarmClass
        ac = self.effective_alarm_class
        # ?Refresh rules ?
        self.rewrite_alarm_class(ac, dry_run=dry_run)

    @property
    def effective_alarm_class(self) -> "AlarmClass":
        """Calculate effective AlarmClass"""
        ac = None
        for w in self.watchers:
            if w.effect == Effect.REWRITE_ALARM_CLASS and "alarm_class" in w.args:
                if isinstance(w.args["alarm_class"], AlarmClass):
                    return w.args["alarm_class"]
                ac = AlarmClass.get_by_id(w.args["alarm_class"])
                break
        return ac or self.alarm_class

    def has_merged_downlinks(self):
        """
        Check if alarm has merged downlinks
        """
        return bool(ActiveAlarm.objects.filter(root=self.id, rca_type=RCA_DOWNLINK_MERGE).first())

    def get_root(self) -> "ActiveAlarm":
        """
        Get top-level root alarm
        """
        root = self
        while root.root:
            root = get_alarm(root.root)
        return root

    def get_summary(self):
        r = {
            "service": SummaryItem.items_to_dict(self.total_services),
            "subscriber": SummaryItem.items_to_dict(self.total_subscribers),
            "object": {},
        }
        if self.managed_object:
            r["object"] = {self.managed_object.object_profile.id: 1}
        if self.is_link_alarm and self.components.interface:
            r["interface"] = {self.components.interface.profile.id: 1}
        return r

    def get_effective_severity(
        self,
        summary: Optional[Dict[str, Any]] = None,
        severity: Optional[int] = None,
        policy: Optional[str] = None,
    ) -> int:
        """
        Calculate Alarm Severities for policy

        Args:
            severity: Alarm Base Severity
            summary: Alarm Affected Summary
            policy:
                * AS - Any Severity
                * CB - Class Based Policy
                * AB - Affected Based Severity Preferred
                * AL - Affected Limit
                * ST - By Tokens

        """
        # if not policy and self.alarm_class.affected_service:
        #    policy = "AB"
        # elif not policy:
        # Base Severity
        if severity:
            base_severity = severity
        elif self.base_severity:
            base_severity = self.base_severity
        elif self.alarm_class.severity:
            base_severity = self.alarm_class.severity.severity
        else:
            base_severity = 1000
        # Getting summary
        summary = summary or self.get_summary()
        effective_severity = None
        policy = policy or self.severity_policy
        match policy:
            case "AB":
                effective_severity = ServiceSummary.get_severity(summary)
            case "AL":
                ss = ServiceSummary.get_severity(summary)
                if base_severity and base_severity >= ss:
                    effective_severity = ss
            case "ST":
                sev = AlarmSeverity.get_from_labels(self.effective_labels)
                if sev:
                    effective_severity = sev.severity
        severity = effective_severity or base_severity
        # Apply limits
        for w in self.watchers:
            if w.effect != Effect.SEVERITY:
                continue
            if w.args.get("min_severity") is not None and severity < w.args["min_severity"]:
                severity = w.args["min_severity"]
            if w.args.get("max_severity") is not None and severity > w.args["max_severity"]:
                severity = w.args["max_severity"]
        return severity

    def update_summary(self, force: bool = False):
        """
        Recalculate all summaries for given alarm.
        Performs recursive descent
        :return:
        """

        def update_dict(d1, d2):
            for k in d2:
                if k in d1:
                    d1[k] += d2[k]
                else:
                    d1[k] = d2[k]

        services = SummaryItem.items_to_dict(self.direct_services)
        subscribers = SummaryItem.items_to_dict(self.direct_subscribers)
        if self.managed_object:
            objects = {self.managed_object.object_profile.id: 1}
        else:
            objects = {}
        if self.is_link_alarm and self.components.interface:
            interface = {self.components.interface.profile.id: 1}
        else:
            interface = {}
        for a in ActiveAlarm.objects.filter(root=self.id):
            a.update_summary()
            update_dict(objects, SummaryItem.items_to_dict(a.total_objects))
            if not self.alarm_class.affected_service:
                # Skip services for calculate Severities
                continue
            update_dict(services, SummaryItem.items_to_dict(a.total_services))
            update_dict(subscribers, SummaryItem.items_to_dict(a.total_subscribers))
        obj_list = ObjectSummaryItem.dict_to_items(objects)
        svc_list = SummaryItem.dict_to_items(services)
        sub_list = SummaryItem.dict_to_items(subscribers)
        if (
            svc_list != self.total_services
            or sub_list != self.total_subscribers
            or obj_list != self.total_objects
            or force
        ):
            self.total_objects = obj_list
            self.total_services = svc_list
            self.total_subscribers = sub_list
            ns = self.get_effective_severity(
                {
                    "service": services,
                    "subscriber": subscribers,
                    "object": objects,
                    "interface": interface,
                },
            )
            if ns != self.severity:
                self.change_severity(severity=ns, to_save=False)
            self.safe_save()

    def _get_path_summary_bulk(self):
        def list_to_dict(summary):
            if not summary:
                return {}
            return {d["profile"]: d["summary"] for d in summary}

        def e_list_to_dict(summary):
            if not summary:
                return {}
            return {d.profile: d.summary for d in summary}

        def dict_to_list(d):
            return [{"profile": k, "summary": d[k]} for k in sorted(d)]

        def get_summary(docs, key, direct=None):
            r = direct.copy() if direct else {}
            for doc in docs:
                dv = doc.get(key)
                if not dv:
                    continue
                for k in dv:
                    nv = dv[k]
                    if nv:
                        r[k] = r.get(k, 0) + nv
            return r

        def get_root_path(alarm_id, path=None):
            path = path or []
            if alarm_id in path:
                raise ValueError("Loop detected: %s" % (str(x) for x in path))
            alarm = alarms.get(alarm_id)
            if not alarm:
                # not in alarms - Alarm in the chain already closed
                return path
            path = [*path, alarm_id]
            root = alarm.get("root")
            if not root or root not in alarms:
                # root not in alarms - Root alarm already closed
                return path
            return get_root_path(root, path)

        alarms = {}  # id -> alarm doc
        children = defaultdict(list)  # id -> [alarm doc, ..]
        # Inject current alarm
        alarms[self.id] = {
            "_id": self.id,
            "root": self.root,
            "severity": self.severity,
            "total_objects": e_list_to_dict(self.total_objects),
            "total_services": e_list_to_dict(self.total_services),
            "total_subscribers": e_list_to_dict(self.total_subscribers),
        }
        # Collect relevant neighbors
        for doc in ActiveAlarm._get_collection().aggregate(
            [
                # Starting from given alarm
                {"$match": {"_id": self.root}},
                # Add to 'path' field all alarm upwards
                {
                    "$graphLookup": {
                        "from": "noc.alarms.active",
                        "connectFromField": "root",
                        "connectToField": "_id",
                        "startWith": "$root",
                        "as": "path",
                        "maxDepth": 50,
                    }
                },
                # Append the necessary fields of given alarm to 'path' field
                # and wipe out all other fields
                {
                    "$project": {
                        "_id": 0,
                        "path": {
                            "$concatArrays": [
                                "$path",
                                [
                                    {
                                        "_id": "$_id",
                                        "root": "$root",
                                        "severity": "$severity",
                                        "direct_services": "$direct_services",
                                        "direct_subscribers": "$direct_subscribers",
                                        "total_objects": "$total_objects",
                                        "total_services": "$total_services",
                                        "total_subscribers": "$total_subscribers",
                                    }
                                ],
                            ]
                        },
                    }
                },
                # Convert path field to the list of documents
                {"$unwind": "$path"},
                # Normalize resulting documents
                {
                    "$project": {
                        "_id": "$path._id",
                        "root": "$path.root",
                        "severity": "$path.severity",
                        "direct_services": "$path.direct_services",
                        "direct_subscribers": "$path.direct_subscribers",
                        "total_objects": "$path.total_objects",
                        "total_services": "$path.total_services",
                        "total_subscribers": "$path.total_subscribers",
                    }
                },
                # Add all children alarms to 'children' field
                {
                    "$lookup": {
                        "from": "noc.alarms.active",
                        "localField": "_id",
                        "foreignField": "root",
                        "as": "children",
                    }
                },
                # Append the neccessary fields of path alarms to `children` field
                # and wipe out all other fields
                {
                    "$project": {
                        "_id": 0,
                        "children": {
                            "$concatArrays": [
                                "$children",
                                [
                                    {
                                        "_id": "$_id",
                                        "root": "$root",
                                        "severity": "$severity",
                                        "direct_services": "$direct_services",
                                        "direct_subscribers": "$direct_subscribers",
                                        "total_objects": "$total_objects",
                                        "total_services": "$total_services",
                                        "total_subscribers": "$total_subscribers",
                                    }
                                ],
                            ]
                        },
                    }
                },
                # Convert path field to the list of documents
                {"$unwind": "$children"},
                # Normalize resulting documents
                {
                    "$project": {
                        "_id": "$children._id",
                        "root": "$children.root",
                        "severity": "$children.severity",
                        "direct_services": "$children.direct_services",
                        "direct_subscribers": "$children.direct_subscribers",
                        "total_objects": "$children.total_objects",
                        "total_services": "$children.total_services",
                        "total_subscribers": "$children.total_subscribers",
                    }
                },
            ]
        ):
            # May contains duplicates, perform deduplication
            doc["direct_services"] = list_to_dict(doc.get("direct_services"))
            doc["direct_subscribers"] = list_to_dict(doc.get("direct_subscribers"))
            doc["total_objects"] = list_to_dict(doc.get("total_objects"))
            doc["total_services"] = list_to_dict(doc.get("total_services"))
            doc["total_subscribers"] = list_to_dict(doc.get("total_subscribers"))
            if doc["_id"] == self.id:
                doc["root"] = self.root
            alarms[doc["_id"]] = doc

        for doc in alarms.values():
            children[doc.get("root")] += [doc]

        # Get path to from current root upwards to global root
        # Check for loops, raise Value error if loop detected
        root_path = get_root_path(self.root)
        bulk = []
        now = datetime.datetime.now()
        for root in root_path:
            doc = alarms[root]
            consequences = children[root]
            total_objects = get_summary(
                consequences,
                "total_objects",
                {self.managed_object.object_profile.id: 1} if self.managed_object else {},
            )
            total_services = get_summary(consequences, "total_services", doc.get("direct_services"))
            total_subscribers = get_summary(
                consequences, "total_subscribers", doc.get("direct_subscribers")
            )
            if (
                doc["total_objects"] != total_objects
                or doc["total_services"] != total_services
                or doc["total_subscribers"] != total_subscribers
            ):
                # Changed
                severity = ServiceSummary.get_severity(
                    {
                        "service": total_services,
                        "subscriber": total_subscribers,
                        "object": total_objects,
                    }
                )
                op = {
                    "$set": {
                        "severity": severity,
                        "total_objects": dict_to_list(total_objects),
                        "total_services": dict_to_list(total_services),
                        "total_subscribers": dict_to_list(total_subscribers),
                    }
                }
                if severity != doc.get("severity"):
                    op["$push"] = {
                        "log": {
                            "timestamp": now,
                            "from_status": "A",
                            "to_status": "A",
                            "message": "Severity changed to %d" % severity,
                        }
                    }
                bulk += [UpdateOne({"_id": root}, op)]
        return bulk

    def set_root(self, root_alarm: "ActiveAlarm", rca_type=RCA_OTHER):
        """
        Set root cause
        """
        if self.root:
            return
        if self.id == root_alarm.id:
            raise Exception("Cannot set self as root cause")
        # Set root
        self.root = root_alarm.id
        self.rca_type = rca_type
        try:
            bulk = self._get_path_summary_bulk()
        except ValueError:
            return  # Loop detected
        bulk += [
            UpdateOne({"_id": self.id}, {"$set": {"root": root_alarm.id, "rca_type": rca_type}})
        ]
        self.log_message("Alarm %s has been marked as root cause" % root_alarm.id, bulk=bulk)
        # self.save()  Saved by log_message
        root_alarm.log_message("Alarm %s has been marked as child" % self.id, bulk=bulk)
        if self.id:
            ActiveAlarm._get_collection().bulk_write(bulk, ordered=True)
        # Bulk
        # root_alarm.touch_watch(is_update=True)

    def reset_root(self):
        """Reset Root cause"""
        self.root = None
        self.log_message("Detached from root for not recovered", to_save=True)
        # Touch only
        # root_alarm.touch_watch(is_update=True)

    def escalate(
        self,
        tt_id,
        close_tt: bool = False,
        wait_tt: Optional[str] = None,
        template: Optional[Template] = None,
        **kwargs,
    ):
        if close_tt:
            self.add_watch(
                Effect.TT_SYSTEM,
                tt_id,
                clear_only=True,
                template=str(template.id) if template else None,
                **kwargs,
            )
        else:
            self.add_watch(
                Effect.TT_SYSTEM,
                tt_id,
                clear_only=False,
                immediate=True,
                template=str(template.id) if template else None,
                **kwargs,
            )
        if wait_tt:
            self.add_watch(Effect.STOP_CLEAR, key=wait_tt, immediate=True)
            self.log_message("Waiting for TT to close")
            call_later(
                "noc.services.escalator.wait_tt.wait_tt",
                scheduler="escalator",
                pool=self.managed_object.escalator_shard,
                alarm_id=self.id,
            )
        self.log_message("Escalated to %s" % tt_id, tt_id=tt_id, to_save=True)
        # q = {"_id": self.id}
        # op = {
        #     "$push": {
        #         "watchers": {
        #             "effect": Effect.TT_SYSTEM.value,
        #             "key": tt_id,
        #             "immediate": True,
        #             "clear_only": True,
        #         }
        #     }
        # }
        # r = ActiveAlarm._get_collection().update_one(q, op)
        # if r.acknowledged and not r.modified_count:
        #     # Already closed, update archive
        #     ArchivedAlarm._get_collection().update_one(q, op)

    def set_escalation_context(self):
        current_context, current_span = get_current_span()
        if current_context or self.escalation_ctx:
            self.escalation_ctx = current_context
            self._get_collection().update_one(
                {"_id": self.id}, {"$set": {"escalation_ctx": current_context}}
            )

    def set_clear_notification(self, notification_group, template):
        self.add_watch(
            Effect.NOTIFICATION_GROUP,
            str(notification_group.id),
            template=str(template.id),
            clear_only=True,
        )
        # self.clear_notification_group = notification_group
        # self.clear_template = template
        self.safe_save(save_condition={"managed_object": {"$exists": True}, "id": self.id})

    def iter_consequences(self) -> Iterable["ActiveAlarm"]:
        """
        Generator yielding all consequences alarm
        """
        for a in ActiveAlarm.objects.filter(root=self.id):
            yield a
            yield from a.iter_consequences()

    def iter_groups(self) -> Iterable["ActiveAlarm"]:
        """
        Generator yielding all groups
        """
        if not self.groups:
            return
        for a in ActiveAlarm.objects.filter(reference__in=self.groups):
            yield a

    def iter_grouped(self) -> Iterable["ActiveAlarm"]:
        """
        Generator yielding all alarm in group
        """
        for a in ActiveAlarm.objects.filter(groups__in=[self.reference]):
            yield a

    def iter_affected(self):
        """
        Generator yielding all affected managed objects
        """
        if self.managed_object:
            seen = {self.managed_object}
            yield self.managed_object
        else:
            seen = {}
        for a in self.iter_consequences():
            if not a.managed_object:
                continue
            if a.managed_object not in seen:
                seen.add(a.managed_object)
                yield a.managed_object

    def iter_escalated(self):
        """
        Generator yielding all escalated consequences
        """
        for a in self.iter_consequences():
            if a.escalation_tt:
                yield a

    @classmethod
    def iter_effective_labels(cls, instance: "ActiveAlarm"):
        yield instance.labels
        yield instance.alarm_class.labels
        if instance.managed_object:
            yield Label.build_expose_labels(
                instance.managed_object.effective_labels, "expose_alarm"
            )

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_alarm")

    def get_matcher_ctx(self) -> Dict[str, Any]:
        r = {
            "alarm_class": str(self.alarm_class.id),
            "labels": list(self.effective_labels),
            "severity": self.severity,
            "reference": getattr(self, "raw_reference", None),
        }
        if self.managed_object:
            r["service_groups"] = list(self.managed_object.effective_service_groups)
        return r

    def get_message_ctx(self, include_affected: bool = True):
        """
        Get escalation context
        """

        def summary_to_list(summary, model):
            r = []
            for k in summary:
                p = model.get_by_id(k.profile)
                if not p or getattr(p, "show_in_summary", True) is False:
                    continue
                r += [{"profile": p.name, "summary": k.summary}]
            return sorted(r, key=lambda x: -x["summary"])

        from noc.sa.models.managedobjectprofile import ManagedObjectProfile
        from noc.sa.models.serviceprofile import ServiceProfile
        from noc.crm.models.subscriberprofile import SubscriberProfile

        if self.managed_object and self.managed_object.segment.is_redundant:
            uplinks = self.managed_object.uplinks
            lost_redundancy = len(uplinks) > 1
            affected_subscribers = summary_to_list(
                self.managed_object.segment.total_subscribers, SubscriberProfile
            )
            affected_services = summary_to_list(
                self.managed_object.segment.total_services, ServiceProfile
            )
        else:
            lost_redundancy = False
            affected_subscribers = []
            affected_services = []
        # Include affected
        if include_affected:
            affected_objects = sorted(self.iter_affected(), key=operator.attrgetter("name"))
        elif self.managed_object:
            affected_objects = [self.managed_object]
        else:
            affected_objects = []
        service = None
        if self.group_type == GroupType.SERVICE and "service" in self.components:
            service = self.components.service
        return {
            "alarm": self,
            # "leader": self.alarm,
            "services": self.affected_services,
            "group": None,
            "service": service,
            "managed_object": self.managed_object,
            "affected_objects": affected_objects,
            "total_objects": summary_to_list(self.total_objects, ManagedObjectProfile),
            "total_subscribers": summary_to_list(self.total_subscribers, SubscriberProfile),
            "total_services": summary_to_list(self.total_services, ServiceProfile),
            "tt": None,
            "lost_redundancy": lost_redundancy,
            "affected_subscribers": affected_subscribers,
            "affected_services": affected_services,
            "has_merged_downlinks": self.has_merged_downlinks(),
        }

    def refresh_escalation_job(
        self, profile: str, is_clear: bool = False, job_id: Optional[str] = None
    ):
        """"""
        from noc.services.correlator.alarmjob import AlarmJob

        if not job_id:
            job = AlarmJob.ensure_profile_job(self, profile)
            if job.is_end:
                # Job already ended
                return
            job.save_state()
            self.add_watch(Effect.ESCALATION, key=profile, job_id=str(job.id))
            job_id = str(job.id)
        # Run Scheduler
        # ts = a.wait_ts - datetime.datetime.now().replace(microsecond=0)
        call_later(
            "noc.services.correlator.alarmjob.run_alarm_job",
            scheduler="correlator",
            max_runs=5,
            pool=config.pool,
            delay=2,
            shard=self.managed_object.id if self.managed_object else 0,
            job_id=job_id,
        )

    def refresh_job(self, is_clear: bool = False, job_id: Optional[str] = None):
        """Refresh Alarm Job by changes"""
        from noc.services.correlator.alarmjob import AlarmJob

        if job_id:
            job = AlarmJob.get_by_id(job_id)
            job.update_item(self, is_clear=is_clear)
        else:
            job = AlarmJob.from_alarm(self, is_clear=is_clear)
        job.run()

    def get_resources(self) -> List[str]:
        """"""
        try:
            return self.components.get_resources()
        except AttributeError:
            return []


@runtime_checkable
class AlarmComponent(Protocol):
    def get_component(self, **kwargs) -> Optional["Generic"]: ...


class ComponentHub(object):
    """
    Resolve Model instance by Alarm Vars data
    If component not find on the system - return None
    If getting component not in AlarmClass - raise AttributeError
    """

    def __init__(
        self, alarm_class: AlarmClass, managed_object: ManagedObject, vars: Dict[str, Any] = None
    ):
        self.logger = logging.getLogger(__name__)
        self.__alarm_class = alarm_class
        self.__managed_object = managed_object
        self.__vars = vars or {}
        self.__components: Dict[str, Any] = {}
        self.__all_components: Optional[Set[str]] = None

    def get_resources(self) -> List[str]:
        """Return resources"""
        r = []
        for c in self.__alarm_class.components:
            res = getattr(self, c.name)
            if res and hasattr(res, "as_resource"):
                r.append(res.as_resource())
        self.__refresh_all_components()
        return r

    def get(self, name: str, default: Optional[Any] = None) -> Optional[Any]:
        if name in self.__components:
            return self.__components[name] if self.__components[name] is not None else default
        self.__refresh_all_components()
        if name not in self.__all_components:
            if default is None:
                raise AttributeError
            return default
        try:
            v = self.__get_component(name)
        except Exception as e:
            self.logger.error("[%s] Error when getting component: %s", name, e)
            v = None
        self.__components[name] = v
        return v if v is not None else default

    def __getitem__(self, name: str) -> Any:
        v = self.get(name)
        if v is None:
            raise KeyError
        return v

    def __getattr__(self, name: str, default: Optional[Any] = None) -> Optional[Any]:
        v = self.get(name)
        # if v is None and default is None:
        #     raise AttributeError
        return default if v is None else v

    def __contains__(self, name: str) -> bool:
        try:
            return self.get(name) is not None
        except AttributeError:
            return False

    def __get_component(self, name: str) -> Optional[Any]:
        for c in self.__alarm_class.components:
            if c.name != name:
                continue
            if c.model.startswith("noc.custom"):
                model = get_handler(c.model)
            else:
                model = get_model(c.model)
            if not isinstance(model, AlarmComponent):
                # Model has not supported component interface
                break
            args = {"managed_object": self.__managed_object}
            for arg in c.args:
                if arg["var"] in self.__vars:
                    args[arg["param"]] = self.__vars[arg["var"]]
            return model.get_component(**args)

    def __refresh_all_components(self) -> None:
        if self.__all_components is not None:
            return
        self.__all_components = {c.name for c in self.__alarm_class.components}


# Avoid circular references
from .archivedalarm import ArchivedAlarm
from .utils import get_alarm
