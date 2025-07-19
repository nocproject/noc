# ----------------------------------------------------------------------
# FM enumerations
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum

# RCA Types
RCA_NONE = 0  # Not correlated
RCA_OTHER = 1  # Unknown/unspecified
RCA_MANUAL = 2  # Correlated manually
RCA_RULE = 2  # Correlated via rule
RCA_TOPOLOGY = 3  # Topology-based correlation
RCA_DOWNLINK_MERGE = 4  # Extended topology/downlink merge


# NOC Event Severity
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


class EventAction(enum.Enum):
    """Event Action.
    * Drop - do not save
    * Ignored - do not disposition
    * Log - Save only
    * Disposition - Create Alarm
    """

    DROP = 1
    LOG = 2
    DISPOSITION = 3
    LOG_ERROR = 4

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class AlarmAction(enum.Enum):
    """
    Attributes:
        ACK: Acknowledge alarm
        UN_ACK: UnAcknowledge alarm
        CLEAR: Clear Alarm
        LOG: Add Alarm Log
        SUBSCRIBE: Subscribe alarm changes
        NOTIFY: Send Notification
    """

    CREATE_TT = "create_tt"
    CLOSE_TT = "close_tt"
    ACK = "ack"
    UN_ACK = "un_ack"
    CLEAR = "clear"  # Reopen
    LOG = "log"
    SUBSCRIBE = "subscribe"
    NOTIFY = "notify"
    HANDLER = "handler"
    SEVERITY = "severity"
    REGISTER_MESSAGE = "register_mx"


class ActionStatus(enum.Enum):
    """
    Action Result Status

    Attributes:
        NEW: new action
        SUCCESS: run success
        FAILED: Failed with error
        WARNING: Warning. Failed, but allowed to fail.
        SKIP: Not running about condition
        PENDING: Pending, waiting for manual approve.
        CANCELLED: Cancelled, not repeat for run / OR Condition
    """

    NEW = "n"
    SUCCESS = "s"
    FAILED = "f"
    WARNING = "w"
    # CANCELLED = "c"
    SKIP = "k"
    PENDING = "p"
    # WAIT_END = "we"
    # STOP = "stop/break"
