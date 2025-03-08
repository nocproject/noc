# ---------------------------------------------------------------------
# Event Message Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List, Dict, Any, Tuple

# Third-party modules
import orjson
from pydantic import BaseModel
from bson import ObjectId

# NOC modules
from noc.core.bi.decorator import bi_hash
from noc.config import config
from noc.core.clickhouse.connect import ClickhouseClient, connection
from noc.core.clickhouse.fields import DateField, DateTimeField
from .enum import EventSeverity, EventSource

MAX_DISPOSE_DELAY = datetime.timedelta(hours=12)

EVENT_QUERY = f"""
    SELECT
        e.event_id as id,
        e.ts as timestamp,
        nullIf(e.event_class, 0) as event_class_bi_id,
        nullIf(e.managed_object, 0) as managed_object_bi_id,
        e.target as target,
        IPv4NumToString(e.ip) as address,
        dictGet('{config.clickhouse.db_dictionaries}.pool', 'name', e.pool) as pool_name,
        dictGetOrNull('{config.clickhouse.db_dictionaries}.eventclass', ('id', 'name'), e.event_class) as event_class,
        dictGetOrNull('{config.clickhouse.db_dictionaries}.profile', 'name', e.profile) as sa_profile,
        e.start_ts as start_timestamp,
        e.source,
        e.severity,
        e.raw_vars,
        e.resolved_vars,
        e.vars,
        e.labels,
        e.message,
        e.snmp_trap_oid,
        e.data
    FROM events e
    WHERE
        event_id = %s
        AND ts BETWEEN %s AND %s
        AND date BETWEEN %s AND %s
    FORMAT JSON
"""

IGNORED_OIDS = {"RFC1213-MIB::sysUpTime.0", "SNMPv2-MIB::sysUpTime.0"}


class Target(BaseModel):
    """
    Attributes:
        address: IP Address message initiator
        name: Name message initiator
        id: For ManagedObject or Agent message Send
        pool: Pool message receiver
        is_agent: Agent message send
        remote_id: Id on remote System that message Send
        service: Service ID (for monitoring integration)
    """

    address: str
    name: str
    id: Optional[str] = None
    pool: Optional[str] = None
    is_agent: bool = False
    remote_id: Optional[str] = None
    service: Optional[str] = None
    # Remote System if used remote_id on other RemoteSystem

    @property
    def reference(self) -> int:
        """
        Calculate target reference
        :return:
        """
        if not self.id:
            return bi_hash((self.pool, self.address))
        return bi_hash(self.id)


class MessageType(BaseModel):
    """
    Description Metadata classification message
    """

    source: EventSource = EventSource.OTHER  # Format for parsed event
    id: Optional[str] = None  # Event type, purpose for format.
    # trap_id for SNMP, event_id for external, code for internal
    severity: EventSeverity = EventSeverity.INDETERMINATE  # Event severity level
    facility: Optional[int] = None  # Event facility (for syslog)
    profile: Optional[str] = None  # Link to SA Profile for classification
    event_class: Optional[str] = None  # For PreClassified message
    level1: Optional[str] = None
    level2: Optional[str] = None
    level3: Optional[str] = None
    # category: Optional[str] = None  # For event category - dot notation
    # AlarmClass ? PreClassify alarm
    # EventClass ? Pre Classify event


class Var(BaseModel):
    name: str  # Variable Name
    value: str  # Variable Value
    scope: Optional[str] = None  # Scope for variable
    snmp_raw: bool = False  # SNMP Raw value

    def __str__(self):
        return f"{self.name}: {self.value}"

    def to_json(self):
        if self.scope:
            return {
                "name": self.name,
                "value": self.value,
                "scope": self.scope,
                "snmp_raw": self.snmp_raw,
            }
        return {"name": self.name, "value": self.value, "snmp_raw": self.snmp_raw}


class Event(BaseModel):
    """
    Message Body Type
    """

    ts: int  # Event Registered ts
    target: Target  # Message Sender Target
    data: List[Var]  # Message Vars
    id: Optional[str] = None
    type: MessageType = MessageType()
    remote_system: Optional[str] = None  # Remote System send event
    remote_id: Optional[str] = None  # Remote Id event on Remote System
    labels: Optional[List[str]] = None  # Event labels
    message: Optional[str] = None  # Event message string
    vars: Optional[Dict[str, Any]] = None  # Event variables

    @property
    def timestamp(self):
        return datetime.datetime.fromtimestamp(self.ts)

    @staticmethod
    def resolve_managed_object_target(bi_id) -> Tuple[str, str]:
        """
        Try resolva ManagedObject for old format event
        :param bi_id:
        :return:
        """
        from noc.sa.models.managedobject import ManagedObject

        mo = ManagedObject.get_by_bi_id(bi_id)
        if mo:
            return str(mo.id), mo.name
        return "", ""

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Event":
        """
        Build instance from clickhouse query
        :param data:
        :return:
        """
        ts = datetime.datetime.fromisoformat(data["timestamp"])
        if "managed_object" in data and isinstance(data["managed_object"], list):
            # For Clickhouse before 23.XXX
            data["managed_object"] = {
                "id": data["managed_object"][0],
                "name": data["managed_object"][1],
            }
        if "event_class" in data and isinstance(data["event_class"], list):
            data["event_class"] = {"id": data["event_class"][0], "name": data["event_class"][1]}
        r = {
            "ts": ts.timestamp(),
            "id": data["id"],
            "labels": data["labels"],
            "message": data["message"],
            "vars": data["vars"],
            "type": {
                "source": data["source"],
                "id": data.get("snmp_trap_oid"),
                "event_class": data["event_class"]["name"],
                "profile": data.get("sa_profile", "Generic.Host"),
            },
        }
        if "severity" in data:
            r["type"]["severity"] = EventSeverity(data["severity"])
        if "target" not in data or not data["target"]:
            r["data"] = [{"name": k, "value": v} for k, v in data["resolved_vars"].items()]
            if data["source"] == "SNMP Trap":
                r["data"] += [
                    {"name": k, "value": v, "snmp_raw": True} for k, v in data["raw_vars"].items()
                ]
            # target
            # Old format
            if not data["managed_object"]["id"] and data["managed_object_bi_id"]:
                mo_id, mo_name = cls.resolve_managed_object_target(data["managed_object_bi_id"])
            else:
                mo_id, mo_name = data["managed_object"]["id"], data["managed_object"]["name"]
            r["target"] = {
                "address": data["address"],
                "name": mo_name,
                "id": mo_id,
                "pool": data["pool_name"],
            }
        else:
            r["target"] = data["target"]
            r["data"] = orjson.loads(data["data"])
        if "id" not in r["target"] and "managed_object" in data:
            r["target"]["id"] = data["managed_object"]["id"]
        if data.get("remote_system"):
            r["remote_system"] = data["remote_system"]
            r["remote_id"] = data["remote_id"]
        return Event.model_validate(r)

    @classmethod
    def get_by_id(
        cls, event_id: str, /, client: ClickhouseClient | None = None
    ) -> Optional["Event"]:
        """

        :param event_id:
        :return:
        """
        event_id = str(ObjectId(event_id))
        # Determine possible date
        oid = ObjectId(event_id)
        ts: datetime.datetime = oid.generation_time.astimezone(config.timezone)
        from_ts = ts - MAX_DISPOSE_DELAY
        to_ts = ts + MAX_DISPOSE_DELAY
        # Make query
        conn = client or connection()
        df = DateField()
        dtf = DateTimeField()
        data = conn.execute(
            EVENT_QUERY,
            args=[
                event_id,
                dtf.to_json(from_ts),
                dtf.to_json(to_ts),
                df.to_json(from_ts),
                df.to_json(to_ts),
            ],
            return_raw=True,
        )
        if not data:
            return None
        # Convert to Event
        res = orjson.loads(data)
        if not res.get("data"):
            return None
        return Event.from_json(res["data"][0])

    @classmethod
    def get_rule(
        cls,
        source: EventSource,
        message: Optional[str] = None,
        labels: Optional[List[str]] = None,
        data: Optional[List[Dict[str, str]]] = None,
        description: Optional[str] = None,
        profile: Optional[str] = None,
        snmp_trap_oid: Optional[str] = None,
    ):
        """
        Create Event Rule by
        Args:
            source:
            message:
            labels:
            data:
            description:
            profile:
            snmp_trap_oid:
        """
        profiles = []
        if profile:
            event_name = " | ".join(profile.split(".")) + f" | <name> ({source.name})"
        else:
            event_name = f"Generic ({source.name})"
        r = {
            "name": event_name,
            "preference": 1000,
            "sources": [source.value],
            "message_rx": message or "",
            "description": description,
            "profiles": profiles,
        }
        if source == EventSource.SYSLOG:
            r["description"] = message
            r["test_cases"] = [{"message": message}]
        elif source == EventSource.SNMP_TRAP and snmp_trap_oid:
            r["description"] = snmp_trap_oid
        patterns = {}
        for k in data:
            if k["name"] in IGNORED_OIDS:
                continue
            if k["name"] not in (
                "collector",
                "facility",
                "severity",
                "syslog_message",
                "message_id",
            ):
                patterns[k["name"]] = k["value"]
        r["patterns"] = [
            {"key_re": "^%s$" % k, "value_re": "^%s$" % patterns[k].strip()} for k in patterns
        ]
        r["labels"] = []
        for ll in labels or []:
            r["labels"].append({"wildcard": ll, "is_required": True})
        return r

    def get_message_context(self, managed_object: Any) -> Dict[str, Any]:
        """"""
        r = {
            "ts": self.timestamp,
            "id": self.id,
            "event_class": self.type.event_class,
            "labels": self.labels,
            "message": self.message,
            "snmp_trap_oid": self.type.id,
            "vars": self.vars,
            "raw_vars": {d.name: d.value for d in self.data},
            "managed_object": managed_object.get_message_context(),
        }
        return r
