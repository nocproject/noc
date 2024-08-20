# ---------------------------------------------------------------------
# ActiveAlarm model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging
import asyncio
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
    IntField,
    LongField,
    ObjectIdField,
    DictField,
    BinaryField,
)
from mongoengine.errors import SaveConditionError

# NOC modules
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.models import get_model
from noc.aaa.models.user import User
from noc.main.models.style import Style
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
from noc.core.fm.enum import RCA_NONE, RCA_OTHER
from noc.core.handler import get_handler
from .alarmseverity import AlarmSeverity
from .alarmclass import AlarmClass
from .alarmlog import AlarmLog
from .escalationprofile import EscalationProfile


@change
class ActiveAlarm(Document):
    meta = {
        "collection": "noc.alarms.active",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "timestamp",
            "root",
            "-severity",
            ("alarm_class", "managed_object"),
            "#reference",
            ("timestamp", "managed_object"),
            "escalation_profile",
            "adm_path",
            "segment_path",
            "container_path",
            "uplinks",
            ("alarm_class", "rca_neighbors"),
            "labels",
            "effective_labels",
            "groups",
            ("root", "groups"),
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
    severity_policy = StringField(default="AS")
    vars = DictField()
    # Alarm reference is a hash of discriminator
    # for external systems
    reference = BinaryField(required=False)
    #
    log = ListField(EmbeddedDocumentField(AlarmLog))
    # Manual acknowledgement timestamp
    ack_ts = DateTimeField(required=False)
    # Manual acknowledgement user name
    ack_user = StringField(required=False)
    #
    opening_event = ObjectIdField(required=False)
    closing_event = ObjectIdField(required=False)
    # List of subscribers
    subscribers = ListField(ForeignKeyField(User))
    #
    custom_subject = StringField(required=False)
    custom_style = ForeignKeyField(Style, required=False)
    #
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
    # Escalated TT ID in form
    # <external system name>:<external tt id>
    escalation_profile: Optional["EscalationProfile"] = PlainReferenceField(EscalationProfile)
    # span context
    escalation_ctx = LongField(required=False)
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
    # Channels
    affected_channels = ListField(ObjectIdField())
    # Uplinks, for topology_rca only
    uplinks = ListField(IntField())
    # RCA neighbor cache, for topology_rca only
    rca_neighbors = ListField(IntField())
    dlm_windows = ListField(IntField())
    # RCA_* enums
    rca_type = IntField(default=RCA_NONE)
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

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_alarm:
            yield "alarm", str(self.id)

    def clean(self):
        super().clean()
        if not self.last_update:
            self.last_update = self.timestamp
        self.adm_path = self.managed_object.adm_path
        self.segment_path = self.managed_object.segment_path
        self.container_path = self.managed_object.container_path
        self.uplinks = self.managed_object.uplinks
        self.rca_neighbors = self.managed_object.rca_neighbors
        self.dlm_windows = self.managed_object.dlm_windows
        self.reopens = self.reopens or 0
        if not self.id:
            # Update effective labels
            self.effective_labels = list(chain.from_iterable(self.iter_effective_labels(self)))

    def safe_save(self, **kwargs):
        """
        Create new alarm or update existing if still exists
        :param kwargs:
        :return:
        """
        if self.id:
            # Update existing only if exists
            if "save_condition" not in kwargs:
                kwargs["save_condition"] = {"id": self.id}
            try:
                self.last_update = datetime.datetime.now().replace(microsecond=0)
                self.save(**kwargs)
                self.register_changes()
            except SaveConditionError:
                pass  # Race condition, closed during update
        else:
            self.save()
            self.register_changes()

    def register_changes(self):
        from noc.fm.models.escalation import Escalation, ItemStatus

        if self.escalation_profile and self.id:
            Escalation.register_item_changes(
                self.id,
                [ItemStatus.CHANGED, ItemStatus.NEW],
                ItemStatus.CHANGED,
            )

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

    def log_message(self, message, to_save=True, bulk=None, source=None):
        if bulk:
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
            )
        ]
        if to_save and not bulk:
            self.safe_save()

    def clear_alarm(self, message, ts=None, force=False, source=None) -> Optional["ArchivedAlarm"]:
        """
        Clear alarm
        :param message: Log clearing message
        :param ts: Clearing timestamp
        :param force: Clear ever if wait_tt seg
        :param source: Source clear alarm
        """
        from .alarmdiagnosticconfig import AlarmDiagnosticConfig
        from .escalation import Escalation, ItemStatus

        if self.alarm_class.is_ephemeral:
            self.delete()
        ts = ts or datetime.datetime.now()
        if self.escalation_profile and self.escalation_profile.alarm_wait_ended and not force:
            self.log_message("Waiting Escalation for TT to close")
            return
        if self.alarm_class.clear_handlers:
            # Process clear handlers
            for h in self.alarm_class.get_clear_handlers():
                try:
                    h(self)
                except Exception:
                    error_report()
        log = self.log + [
            AlarmLog(timestamp=ts, from_status="A", to_status="C", message=message, source=source)
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
            escalation_profile=self.escalation_profile.id if self.escalation_profile else None,
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
        ct = self.alarm_class.get_control_time(self.reopens)
        if ct:
            a.control_time = datetime.datetime.now() + datetime.timedelta(seconds=ct)
        a.save()
        # Send notifications
        # f not a.root and not self.reopens:
        #    a.managed_object.event(
        #        a.managed_object.EV_ALARM_CLEARED,
        #        {
        #            "alarm": a,
        #            "subject": a.subject,
        #            "body": a.body,
        #            "symptoms": a.alarm_class.symptoms,
        #            "recommended_actions": a.alarm_class.recommended_actions,
        #            "probable_causes": a.alarm_class.probable_causes,
        #        },
        #    )
        # elif ct:
        #     pass
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
        # Refresh Services
        if self.affected_services:
            defer(
                "noc.sa.models.service.refresh_service_status",
                svc_ids=[str(x) for x in self.affected_services],
            )
        # Close TT
        # MUST be after .delete() to prevent race conditions
        if self.escalation_profile:
            Escalation.register_item_changes(self.id, [ItemStatus.NEW], ItemStatus.REMOVED)
        # Gather diagnostics
        AlarmDiagnosticConfig.on_clear(a)
        # Return archived
        return a

    def get_template_vars(self) -> Dict[str, Any]:
        """
        Prepare template variables
        """
        vars = self.vars.copy()
        vars.update({"alarm": self})
        return vars

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
        s = Jinja2Template(self.alarm_class.body_template).render(self.get_template_vars())
        return s

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
        if user.id not in self.subscribers:
            self.subscribers += [user.id]
            self.log_message(
                "%s(%s): has been subscribed"
                % ((" ".join([user.first_name, user.last_name]), user.username)),
                to_save=False,
                source=user.username,
            )
            self.save()

    def unsubscribe(self, user: "User"):
        if self.is_subscribed(user):
            self.subscribers = [u.id for u in self.subscribers if u != user.id]
            self.log_message(
                "%s(%s) has been unsubscribed"
                % ((" ".join([user.first_name, user.last_name]), user.username)),
                to_save=False,
                source=user.username,
            )
            self.save()

    def is_subscribed(self, user: "User"):
        return user.id in self.subscribers

    @property
    def is_link_alarm(self) -> bool:
        return hasattr(self.components, "interface")

    def acknowledge(self, user: "User", msg=""):
        self.ack_ts = datetime.datetime.now()
        self.ack_user = user.username
        self.log = self.log + [
            AlarmLog(
                timestamp=self.ack_ts,
                from_status="A",
                to_status="A",
                message="Acknowledged by %s(%s): %s" % (user.get_full_name(), user.username, msg),
                source=user.username,
            )
        ]
        self.safe_save()

    def unacknowledge(self, user: "User", msg=""):
        self.ack_ts = None
        self.ack_user = None
        self.log = self.log + [
            AlarmLog(
                timestamp=datetime.datetime.now(),
                from_status="A",
                to_status="A",
                message="Unacknowledged by %s(%s): %s" % (user.get_full_name(), user.username, msg),
                source=user.username,
            )
        ]
        self.safe_save()

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

        #
        fm_pool = self.managed_object.get_effective_fm_pool()
        stream = f"dispose.{fm_pool.name}"
        service = get_service()
        num_partitions = asyncio.run(service.get_stream_partitions(stream))
        partition = int(self.managed_object.id) % num_partitions
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
            partition=partition,
        )

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
        else:
            return AlarmSeverity.get_severity(self.severity).style

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
            "objects": {self.managed_object.object_profile.id: 1},
        }
        if self.is_link_alarm and self.components.interface:
            r["interface"] = {self.components.interface.profile.id: 1}
        return r

    def get_effective_severity(
        self,
        summary: Optional[Dict[str, Any]] = None,
        severity: Optional[AlarmSeverity] = None,
        policy: Optional[str] = None,
    ) -> int:
        """
        Calculate Alarm Severities for policy

        Args:
            severity: Alarm Based Severity
            summary: Alarm Affected Summary
            policy:
                * AS - Any Severity
                * CB - Class Based Policy
                * AB - Affected Based Severity Preferred
                * AL - Affected Limit
                * ST - By Tokens

        """
        if not policy and self.alarm_class.affected_service:
            policy = "AB"
        elif not policy:
            policy = self.severity_policy

        if severity:
            severity = severity.severity
        elif self.base_severity:
            severity = self.base_severity
        elif self.alarm_class.severity:
            severity = self.alarm_class.severity.severity
        else:
            severity = 1000
        summary = summary or self.get_summary()
        match policy:
            case "CB":
                return severity
            case "AB":
                return ServiceSummary.get_severity(summary)
            case "AL":
                ss = ServiceSummary.get_severity(summary)
                if severity and severity <= ss:
                    return severity
                return ss
            case "ST":
                sev = AlarmSeverity.get_from_labels(self.effective_labels)
                if sev:
                    return sev.severity
        return severity

    def update_summary(self):
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
        objects = {self.managed_object.object_profile.id: 1}
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
        ):
            self.total_objects = obj_list
            self.total_services = svc_list
            self.total_subscribers = sub_list
            ns = self.get_effective_severity(
                {
                    "service": services,
                    "subscriber": subscribers,
                    "objects": objects,
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
            path = path + [alarm_id]
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
                consequences, "total_objects", {self.managed_object.object_profile.id: 1}
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

    def set_root(self, root_alarm, rca_type=RCA_OTHER):
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

    def escalate(self, escalation):
        self.escalation_profile = escalation.profile
        self.log_message("Escalated as %s" % escalation)
        q = {"_id": self.id}
        op = {
            "$set": {
                "escalation_profile": self.escalation_profile.id,
            }
        }
        r = ActiveAlarm._get_collection().update_one(q, op)
        if r.acknowledged and not r.modified_count:
            # Already closed, update archive
            ArchivedAlarm._get_collection().update_one(q, op)

    def set_escalation_context(self):
        current_context, current_span = get_current_span()
        if current_context or self.escalation_ctx:
            self.escalation_ctx = current_context
            self._get_collection().update_one(
                {"_id": self.id}, {"$set": {"escalation_ctx": current_context}}
            )

    def set_clear_notification(self, notification_group, template):
        self.clear_notification_group = notification_group
        self.clear_template = template
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
        seen = {self.managed_object}
        yield self.managed_object
        for a in self.iter_consequences():
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
        yield [
            ll
            for ll in instance.managed_object.effective_labels
            if Label.get_effective_setting(ll, "expose_alarm")
        ]

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_alarm")


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
        return self.get(name) is not None

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
