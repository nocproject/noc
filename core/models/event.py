# ---------------------------------------------------------------------
# Event Message Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import enum
import datetime
from typing import Optional, List, Dict, Any, Tuple

# Third-party modules
import orjson
from pydantic import BaseModel

# NOC modules
from noc.core.bi.decorator import bi_hash
from noc.config import config


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
        dictGetOrNull('{config.clickhouse.db_dictionaries}.managedobject', ('id', 'name'), e.managed_object) as managed_object,
        e.start_ts as start_timestamp,
        e.source, e.raw_vars, e.resolved_vars, e.vars, e.labels, e.message, e.data,
        d.alarms as alarms
    FROM events e
        LEFT OUTER JOIN (
            SELECT event_id, groupArray(alarm_id) as alarms FROM disposelog  WHERE event_id=%s AND alarm_id != '' GROUP BY event_id) as d
        ON e.event_id == d.event_id
    WHERE event_id=%s
    FORMAT JSON
"""


class EventSeverity(enum.Enum):
    # Bind color, Bind glif
    IGNORED = -1
    CLEARED = 0
    INDETERMINATE = 1
    WARNING = 2
    MINOR = 3
    MAJOR = 4
    CRITICAL = 5


# ITUPerceivedSeverity to Syslog SEVERITY Mapping, rfc5674
SEVERITY_MAP = {
    0: EventSeverity.CRITICAL,
    1: EventSeverity.CRITICAL,
    2: EventSeverity.MAJOR,
    3: EventSeverity.MINOR,
    4: EventSeverity.WARNING,
    5: EventSeverity.INDETERMINATE,
    6: EventSeverity.INDETERMINATE,
    7: EventSeverity.IGNORED,
}


class SyslogSeverity(enum.Enum):
    @property
    def noc_severity(self):
        return SEVERITY_MAP[self.value]

    EMERGENCY = 0  # System is unusable
    ALERT = 1  # Action must be taken immediately
    CRITICAL = 2  # Critical conditions
    ERROR = 3  # Error conditions
    WARNING = 4  # Warning conditions
    NOTICE = 5  # Normal but significant conditions
    INFORMATIONAL = 6  # Informational messages
    DEBUG = 7  # Debug-level messages


class EventSource(enum.Enum):
    SYSLOG = "syslog"
    SNMP_TRAP = "SNMP Trap"
    SYSTEM = "system"
    INTERNAL = "internal"
    WINEVENT = "winevent"
    OTHER = "other"


class Target(BaseModel):
    address: str  # IP Address message initiator
    name: str  # Name message initiator
    id: Optional[str] = None  # For ManagedObject or Agent message Send
    pool: Optional[str] = None  # Pool message receiver
    is_agent: bool = False  # Agent message send
    remote_id: Optional[str] = None  # Id on remote System that message Send
    service: Optional[str] = None  # Service ID (for monitoring integration) ?

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
    facility: Optional[str] = None  # Event facility (for syslog)
    profile: Optional[str] = None  # Link to SA Profile for classification
    event_class: Optional[str] = None  # For PreClassified message
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
            },
        }
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
        if "id" not in r["target"] and data["managed_object"]["id"]:
            r["target"]["id"] = data["managed_object"]["id"]
        if data.get("remote_system"):
            r["remote_system"] = data["remote_system"]
            r["remote_id"] = data["remote_id"]
        return Event.model_validate(r)

    @classmethod
    def get_event_by_id(cls, event_id: str) -> Optional["Event"]:
        """

        :param event_id:
        :return:
        """
        from noc.core.clickhouse.connect import connection

        cursor = connection()
        res = orjson.loads(cursor.execute(EVENT_QUERY, args=[event_id, event_id], return_raw=True))
        if res:
            return Event.from_json(res["data"][0])
        return
