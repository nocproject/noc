# ----------------------------------------------------------------------
# @diagnostic decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
import datetime
import logging
import itertools
from dataclasses import dataclass
from collections import defaultdict
from functools import partial
from typing import Optional, List, Dict, Any, Iterable, Tuple

# Third-party modules
import orjson
from pydantic import BaseModel, PrivateAttr

# NOC modules
from noc.core.ioloop.util import run_sync
from noc.core.checkers.base import Check, CheckResult, MetricValue
from noc.core.handler import get_handler
from noc.config import config
from noc.models import is_document


EVENT_TRANSITION = {
    "disable": {"unknown": "blocked", "enabled": "blocked", "failed": "blocked"},
    "fail": {"unknown": "failed", "enabled": "failed"},
    "ok": {"unknown": "enabled", "failed": "enabled"},
    "allow": {"blocked": "unknown"},
    "expire": {"enabled": "unknown", "failed": "unknown"},
}

# BuiltIn Diagnostics
SA_DIAG = "SA"
EVENT_DIAG = "FM_EVENT"
ALARM_DIAG = "FM_ALARM"
TT_DIAG = "TT"
#
SNMP_DIAG = "SNMP"
PROFILE_DIAG = "Profile"
CLI_DIAG = "CLI"
HTTP_DIAG = "HTTP"
SYSLOG_DIAG = "SYSLOG"
SNMPTRAP_DIAG = "SNMPTRAP"
#
DIAGNOCSTIC_LABEL_SCOPE = "diag"


def json_default(obj):
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    elif isinstance(obj, datetime.datetime):
        return obj.replace(microsecond=0).isoformat(sep=" ")
    raise TypeError


class DiagnosticEvent(str, enum.Enum):
    disable = "disable"
    fail = "fail"
    ok = "ok"
    allow = "allow"
    expire = "expire"

    def get_state(self, state: "DiagnosticState") -> Optional["DiagnosticState"]:
        if state.value not in EVENT_TRANSITION[self.value]:
            return
        return DiagnosticState(EVENT_TRANSITION[self.value][state.value])


class DiagnosticState(str, enum.Enum):
    unknown = "unknown"
    blocked = "blocked"
    enabled = "enabled"
    failed = "failed"

    def fire_event(self, event: str) -> "DiagnosticState":
        return DiagnosticEvent(event).get_state(self)

    @property
    def is_blocked(self) -> bool:
        return self.value == "blocked"

    @property
    def is_active(self) -> bool:
        return self.value != "blocked" and self.value != "unknown"


@dataclass(frozen=True)
class DiagnosticConfig(object):
    """
    Attributes:
        diagnostic: Name configured diagnostic
        blocked: Block by config flag
        default_state: Default DiagnosticState
        checks: Configured diagnostic checks
        diagnostic_handler: Diagnostic result handler
        dependent: Dependency diagnostic
    """

    diagnostic: str
    blocked: bool = False
    default_state: DiagnosticState = DiagnosticState.unknown
    # Check config
    checks: Optional[List[Check]] = None
    diagnostic_handler: Optional[str] = None
    dependent: Optional[List[str]] = None
    # ANY - Any check has OK, ALL - ALL checks has OK
    state_policy: str = "ANY"  # Calculate State on checks.
    reason: Optional[str] = None  # Reason current state
    # Discovery Config
    run_policy: str = "A"  # A - Always, M - manual, F - Unknown or Failed, D - Disable
    run_order: str = "S"  # S - Before all discovery, E - After all discovery
    discovery_box: bool = False  # Run on periodic discovery
    discovery_periodic: bool = False  # Run on box discovery
    #
    save_history: bool = False
    # Display Config
    show_in_display: bool = True  # Show diagnostic on UI
    display_description: Optional[str] = None  # Description for show User
    display_order: int = 0  # Order on displayed list
    # FM Config
    alarm_class: Optional[str] = None  # Default AlarmClass for raise alarm
    alarm_labels: Optional[List[str]] = None


DIAGNOSTIC_CHECK_STATE: Dict[bool, DiagnosticState] = {
    True: DiagnosticState("enabled"),
    False: DiagnosticState("failed"),
}


class CheckStatus(BaseModel):
    """
    Attributes:
        name: Check name
        status: Check execution result, True - OK, False - Fail
        arg0: Check params
        skipped: Check execution was skipped
        error: Error description for Fail status
    """

    name: str
    status: bool
    arg0: Optional[str] = None
    skipped: bool = False
    error: Optional[str] = None

    @classmethod
    def from_result(cls, cr: CheckResult) -> "CheckStatus":
        return CheckStatus(
            name=cr.check,
            status=cr.status,
            skipped=cr.skipped,
            error=cr.error.message if cr.error else None,
            arg0=cr.arg0,
        )


class DiagnosticHandler:
    """
    Run diagnostic by config and check status
    """

    def __init__(self, cfg: DiagnosticConfig, labels: Optional[List[str]] = None):
        self.config = cfg
        self.labels = labels

    def iter_checks(self) -> Iterable[Tuple[Check, ...]]:
        """Iterate over checks"""

    def get_result(
        self, checks: List[CheckResult]
    ) -> Tuple[Optional[bool], Optional[str], Dict[str, Any]]:
        """Getting Diagnostic result"""


class DiagnosticItem(BaseModel):
    """Class for Diagnostic Result description"""

    diagnostic: str
    state: DiagnosticState = DiagnosticState("unknown")
    checks: Optional[List[CheckStatus]] = None
    # scope: Literal["access", "all", "discovery", "default"] = "default"
    # policy: str = "ANY
    reason: Optional[str] = None
    changed: Optional[datetime.datetime] = None
    _config: Optional[DiagnosticConfig] = PrivateAttr()
    _handler: Optional[DiagnosticHandler] = PrivateAttr()
    _active_checks: Optional[List[Tuple[Check, ...]]] = None

    def __init__(self, config: Optional[DiagnosticConfig] = None, **data):
        super().__init__(**data)
        self._config = config

    @property
    def config(self):
        return self._config

    def reset(self, reason="Reset by"):
        if self.config.blocked:
            self.state = DiagnosticState.blocked
            self.reason = self.config.reason
        else:
            self.state = self.config.default_state
            self.reason = reason
        self.checks = []
        self.changed = datetime.datetime.now()

    def get_handler(self, **kwargs) -> DiagnosticHandler:
        if not hasattr(self, "_handler"):
            h = get_handler(self.config.diagnostic_handler)
            if not h:
                raise AttributeError("Unknown Diagnostic Handler")
            self._handler = h(**kwargs)
        return self._handler

    def iter_checks(self, **kwargs) -> Iterable[Tuple[Check, ...]]:
        """Iterate over checks"""
        if not self.config.diagnostic_handler and not self.config.checks:
            return
        elif not self.config.diagnostic_handler:
            yield tuple(self.config.checks)
            return
        h = self.get_handler(**kwargs)
        yield from h.iter_checks()

    def get_check_status(
        self, checks: List[CheckResult]
    ) -> Tuple[Optional[bool], Optional[str], Dict[str, Any]]:
        """
        Calculate check status, ANY or ALL policy apply
        """
        if self.config.diagnostic_handler:
            h = self.get_handler()
            return h.get_result(checks)
        self.checks = [CheckStatus.from_result(c) for c in checks]
        state = None
        data = {}
        for c in self.checks:
            if c.skipped:
                continue
            if not c and self.config.state_policy == "ALL":
                state = False
                break
            if c and self.config.state_policy == "ANY":
                state = True
                break
        return state, None, data


class DiagnosticHub(object):
    """
    Diagnostic Hub
    Methods:
    * Configured Diagnostic - state detected config only - unknown -> blocked
    * Checked Diagnostic - state detected as checks -> unknown -> blocked -> enable -> failed
    * set_diagnostic for change diagnostic state ? state/checks
    * reset_diagnostic - delete diagnostic record from field - as Unknown state

    * sync_diagnostic - check diagnostic state, and update it
    ? question - update depended diagnostic
    Discovery update only checks on diagnostic, after in - run sync_diagnostic
    ? update_diagnostic_checks
    ? Custom diagnostic - change labels: reset diagnostic by not match current label
    ? Change affected config ? can_XXXXX method, -
        can_block_diagnostic(<name>) -> return True/False, reason ... blocked, reason

    Depended - if high diagnostic blocked - blocks low

    """

    def __init__(
        self,
        o: Any,
        dry_run: bool = False,
        sync_alarm: bool = True,
        sync_labels: bool = True,
        logger=None,
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.__diagnostics: Optional[Dict[str, DiagnosticItem]] = None  # Actual diagnostic state
        self.__checks: Dict[str, List[str]] = None
        self.__depended: Dict[str, str] = {}  # Depended diagnostics
        if not hasattr(o, "diagnostics"):
            raise NotImplementedError("Diagnostic Interface not supported")
        self.__object = o
        self.__data: Dict[str, Any] = {}
        self.dry_run: bool = dry_run  # For test do not DB Sync
        self.sync_alarm = sync_alarm
        self.sync_labels = sync_labels
        self.bulk_mode: bool = False
        # diagnostic state

    def get(self, name: str) -> Optional[DiagnosticItem]:
        if self.__diagnostics is None:
            self.__load_diagnostics()
        if name in self.__diagnostics:
            return self.__diagnostics[name]

    def __getitem__(self, name: str) -> "DiagnosticItem":
        v = self.get(name)
        if v is None:
            raise KeyError
        return v

    def __getattr__(self, name: str, default: Optional[Any] = None) -> Optional["DiagnosticItem"]:
        v = self.get(name)
        if v is None:
            raise AttributeError(f"Unknown diagnostic {name}")
        return v

    def __contains__(self, name: str) -> bool:
        return self.get(name) is not None

    def __enter__(self):
        """
        Bulk mode. Sync diagnostic after exit from context
        """
        self.bulk_mode = True
        self.bulk_changes = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bulk_mode = False
        if not self.bulk_changes:
            self.bulk_changes = 0
            return
        self.sync_diagnostics()
        # Hack for refresh diagnostic Hub on object
        # For fix it may be use set __diagnostics to object diagnostic
        self.__object.diagnostic.__diagnostics = None

    def __iter__(self) -> Iterable[DiagnosticItem]:
        if self.__diagnostics is None:
            self.__load_diagnostics()
        for d in self.__diagnostics.values():
            yield d

    def has_active_diagnostic(self, name: str) -> bool:
        """
        Check diagnostic has worked: Enabled or Failed state
        :param name:
        :return:
        """
        d = self.get(name)
        if d is None:
            return False
        if d.state == DiagnosticState.enabled or d.state == DiagnosticState.failed:
            return True
        return False

    def get_object_diagnostic(self, name: str) -> Optional[DiagnosticItem]:
        """
        Get DiagnosticItem from Object
        Args:
            name: Diagnostic Name
        """
        if name in self.__object.diagnostics:
            return DiagnosticItem(**self.__object.diagnostics[name])
        return DiagnosticItem(diagnostic=name)

    def iter_diagnostic_configs(self) -> Iterable[DiagnosticConfig]:
        for d in self:
            yield d.config

    def __load_diagnostics(self):
        """Loading Diagnostic from Object Config"""
        r = {}
        if is_document(self.__object):
            return
        for dc in self.__object.iter_diagnostic_configs():
            item = self.__object.diagnostics.get(dc.diagnostic) or {}
            if not item:
                item = {"diagnostic": dc.diagnostic, "state": dc.default_state.value}
            r[dc.diagnostic] = DiagnosticItem(config=dc, **item)
            if r[dc.diagnostic].state == DiagnosticState.blocked and not dc.blocked:
                r[dc.diagnostic].state = dc.default_state
            elif dc.blocked:
                r[dc.diagnostic].state = DiagnosticState.blocked
                if dc.reason:
                    r[dc.diagnostic].reason = dc.reason
            # item["config"] = dc
            for dd in dc.dependent or []:
                self.__depended[dd] = dc.diagnostic
        self.__diagnostics = r

    def __load_checks(self):
        """"""
        self.__checks = defaultdict(list)
        for di in self.__diagnostics.values():
            for checks in di.iter_checks(
                cfg=di.config,
                labels=self.__object.effective_labels,
                logger=self.logger,
                address=self.__object.address,
                cred=self.__object.credentials.get_snmp_credential(),
                profile=self.__object.profile.name,
            ):
                if di._active_checks is None:
                    di._active_checks = []
                di._active_checks.append(checks)
                for c in itertools.chain(checks):
                    self.__checks[c.key] += [di.diagnostic]

    def iter_active_checks(self, d: str) -> Iterable[Tuple[Check, ...]]:
        if self.__checks is None:
            self.__load_checks()
        di = self.get(d)
        yield from di._active_checks

    def set_state(
        self,
        diagnostic: str,
        state: DiagnosticState = DiagnosticState("unknown"),
        reason: Optional[str] = None,
        changed_ts: Optional[datetime.datetime] = None,
        data: Optional[Dict[str, Any]] = None,
    ):
        """
        Set diagnostic ok/fail state
        Args:
            diagnostic: Diagnostic Name
            state: True - Enabled; False - Failed
            reason: Reason state changed
            changed_ts: Timestamp changed
            data: Collected checks data
        """
        d = self[diagnostic]
        if d.state.is_blocked or d.state == state:
            self.logger.debug("[%s] State is same", d.diagnostic)
            return
        self.logger.info(
            "[%s] Change diagnostic state: %s -> %s", diagnostic, d.state.value, state.value
        )
        # last_state = d.state
        d.changed = changed_ts or datetime.datetime.now()
        d.changed = d.changed.replace(microsecond=0, tzinfo=None)
        d.state = state
        d.reason = reason
        # Update dependent
        if d.diagnostic not in self.__depended:
            self.sync_diagnostics()
            return
        self.logger.debug("[%s] Update depended diagnostic", d.diagnostic)
        d = self[self.__depended[d.diagnostic]]
        states = []
        for dd in d.config.dependent:
            if dd in self:
                states.append(self[dd].state)
        if d.config.state_policy == "ANY" and DiagnosticState.enabled not in states:
            self.set_state(d.diagnostic, DiagnosticState.failed)
        elif d.config.state_policy == "ALL" and DiagnosticState.failed in states:
            self.set_state(d.diagnostic, DiagnosticState.failed)
        else:
            self.set_state(d.diagnostic, DiagnosticState.enabled)
        self.sync_diagnostics()

    def update_checks(self, checks: List[CheckResult]):
        """
        Update checks on diagnostic and calculate state
        * Map diagnostic -> checks
        * Calculate state
        * Set state
        """
        now = datetime.datetime.now().replace(microsecond=0)
        affected_diagnostics: Dict[str, List[CheckResult]] = defaultdict(list)
        if not self.__checks:
            self.__load_checks()
        metrics = []
        for cr in checks:
            if cr.key not in self.__checks:
                self.logger.debug(
                    "[%s|%s] Diagnostic not enabled: %s", cr.check, cr.key, self.__checks
                )
                continue
            if cr.metrics:
                metrics += cr.metrics
            m_labels = [f"noc::check::name::{cr.check}"]
            if cr.args:
                m_labels += [f"noc::check::arg0::{cr.arg}"]
            if cr.address:
                m_labels += [f"noc::check::address::{cr.address}"]
            for d in self.__checks[cr.key]:
                affected_diagnostics[d] += [cr]
                if not cr.skipped:
                    metrics += [
                        MetricValue(
                            "Check | Status",
                            value=int(cr.status),
                            labels=m_labels + [f"noc::diagnostic::{d}"],
                        )
                    ]
        # Calculate State and Update diagnostic
        for d, crs in affected_diagnostics.items():
            c_state, c_reason, c_data = self[d].get_check_status(crs)
            if c_state is None:
                # Partial, more checks needed
                continue
            self.set_state(
                d,
                DIAGNOSTIC_CHECK_STATE[c_state],
                reason=c_reason,
                changed_ts=now,
                data=c_data,
            )
        if metrics:
            self.register_diagnostic_metrics(metrics)

    def refresh_diagnostics(self):
        """
        Reload diagnostic config and sync
        """
        self.__diagnostics = None
        self.sync_diagnostics()

    def reset_diagnostics(
        self, diagnostics: List[str], reason: Optional[str] = "By Reset Diagnostic"
    ):
        """
        Reset diagnostic data.
        * update config for resetting diagnostic
        * synchronize diagnostics config
        """
        if isinstance(diagnostics, str):
            raise AttributeError("Diagnostics must be List")
        self.logger.info("[%s] Reset diagnostics: %s", str(self.__object), diagnostics)
        for d in diagnostics:
            if d in self:
                self[d].reset(reason=reason)
        self.sync_diagnostics()

    def sync_diagnostics(self):
        """
        Sync diagnostics with object
        * sync state
        * register change
        * sync alarms
        * save database
        * clear cache
        """
        if self.bulk_mode:
            self.logger.debug("Bulk mode. Sync blocked")
            self.bulk_changes += 1
            return
        changed_state = set()
        updated = []
        for d_new in self:
            d_name = d_new.diagnostic
            d_current = self.get_object_diagnostic(d_name)
            # Diff
            if d_current == d_new:
                self.logger.debug("[%s] Diagnostic Same, next.", d_name)
                continue
            self.logger.info("[%s] Update object diagnostic", d_name)
            if d_current.state != d_new.state:
                if (
                    d_current.state == DiagnosticState.failed
                    or d_new.state == DiagnosticState.failed
                ):
                    changed_state.add(d_name)
                self.register_diagnostic_change(
                    d_name,
                    state=d_new.state,
                    from_state=d_current.state,
                    reason=d_new.reason,
                    ts=d_new.changed,
                )
            self.__object.diagnostics[d_name] = d_new.model_dump()
            updated += [d_new]
        removed = set(self.__object.diagnostics) - set(self.__diagnostics)
        if changed_state:
            self.sync_alarms(list(changed_state))
        if updated or removed:
            self.__object.effective_labels = list(
                sorted(
                    [
                        ll
                        for ll in self.__object.effective_labels
                        if not ll.startswith(DIAGNOCSTIC_LABEL_SCOPE)
                    ]
                    + [
                        f"{DIAGNOCSTIC_LABEL_SCOPE}::{d.diagnostic}::{d.state}"
                        for d in self.__diagnostics.values()
                    ]
                )
            )
            self.sync_with_object(updated, list(removed))

    def sync_with_object(
        self,
        update: Optional[List[DiagnosticItem]],
        remove: Optional[List[str]] = None,
        sync_labels: bool = True,
    ):
        """
        Sync diagnostics state with object
        """
        from django.db import connection as pg_connection

        if self.dry_run or is_document(self.__object):
            return
        params = []
        query_set = ""
        if remove:
            self.logger.debug("[%s] Removed diagnostics", list(remove))
            params += remove
            query_set += " - %s" * len(remove)
        if update:
            self.logger.debug("[%s] Update diagnostics", list(update))
            diags = {d.diagnostic: d.model_dump(exclude={"config"}) for d in update}
            params += [orjson.dumps(diags, default=json_default).decode("utf-8")]
            query_set += " || %s::jsonb"
        if not params:
            return
        if sync_labels:
            params += [list(self.__object.effective_labels)]
            query_set += ",effective_labels=%s::varchar[]"
        params += [self.__object.id]
        with pg_connection.cursor() as cursor:
            self.logger.debug("[%s] Saving changes", list(update))
            cursor.execute(
                f"""
                 UPDATE sa_managedobject
                 SET diagnostics = diagnostics {query_set}
                 WHERE id = %s""",
                params,
            )
        self.__object._reset_caches(self.__object.id)

    def sync_alarms(self, diagnostics: Optional[List[str]] = None, alarm_disable: bool = False):
        """
        Raise & clear Alarm for diagnostic. Only diagnostics with alarm_class set will be synced.
        If diagnostics param is set and alarm_class is not set - clear alarm
         For dependent - Group alarm base on diagnostic with alarm for depended
        :param diagnostics: If set - sync only params diagnostic and depends
        :param alarm_disable: Disable alarm by settings. Clear active alarm
        :return:
        """
        from noc.core.service.loader import get_service

        now = datetime.datetime.now()
        # Group Alarms
        groups = {}
        #
        alarms = {}
        alarm_config: Dict[str, Dict[str, Any]] = {}  # diagnostic -> AlarmClass Map
        messages: List[Dict[str, Any]] = []  # Messages for send dispose
        processed = set()
        diagnostics = set(diagnostics or [])
        for d in self:
            d_name = d.diagnostic
            dc = d.config
            if not dc.alarm_class:
                continue
            alarm_config[dc.diagnostic] = {
                "alarm_class": dc.alarm_class,
                "alarm_labels": dc.alarm_labels or [],
            }
            if d_name in processed:
                continue
            if diagnostics and not dc.dependent and dc.diagnostic not in diagnostics:
                # Skip non-changed diagnostics
                continue
            if diagnostics and dc.dependent and not diagnostics.intersection(set(dc.dependent)):
                # Skip non-affected depended diagnostics
                continue
            if dc.dependent:
                groups[dc.diagnostic] = []
                for d_name in dc.dependent:
                    if d_name not in self:
                        continue
                    dd = self[d_name]
                    if (
                        dd
                        and dd.state == DiagnosticState.failed
                        and self.sync_alarm
                        and not alarm_disable
                    ):
                        groups[dc.diagnostic] += [{"diagnostic": d_name, "reason": dd.reason or ""}]
                    processed.add(d_name)
            elif d and d.state == d.state.failed and self.sync_alarm and not alarm_disable:
                alarms[dc.diagnostic] = {
                    "timestamp": now,
                    "reference": f"dc:{self.__object.id}:{d.diagnostic}",
                    "managed_object": str(self.__object.id),
                    "$op": "raise",
                    "alarm_class": dc.alarm_class,
                    "labels": dc.alarm_labels or [],
                    "vars": {"reason": d.reason or ""},
                }
            else:
                alarms[dc.diagnostic] = {
                    "timestamp": now,
                    "reference": f"dc:{self.__object.id}:{dc.diagnostic}",
                    "$op": "clear",
                }
        # Group Alarm
        for d in groups:
            messages += [
                {
                    "$op": "ensure_group",
                    "reference": f"dc:{d}:{self.__object.id}",
                    "alarm_class": alarm_config[d]["alarm_class"],
                    "alarms": [
                        {
                            "reference": f'dc:{dd["diagnostic"]}:{self.__object.id}',
                            "alarm_class": alarm_config[dd["diagnostic"]]["alarm_class"],
                            "managed_object": str(self.__object.id),
                            "timestamp": now,
                            "labels": alarm_config[dd["diagnostic"]]["alarm_labels"],
                            "vars": {"reason": dd["reason"] or ""},
                        }
                        for dd in groups[d]
                    ],
                }
            ]
        # Other
        for d in alarms:
            if d in processed:
                continue
            messages += [alarms[d]]
        if self.dry_run:
            self.logger.info("Sync Diagnostic Alarm: %s", messages)
            return
        # Send Dispose
        svc = get_service()
        for msg in messages:
            stream, partition = self.__object.alarms_stream_and_partition
            svc.publish(
                orjson.dumps(msg),
                stream=stream,
                partition=partition,
            )
            self.logger.debug(
                "Dispose: %s", orjson.dumps(msg, option=orjson.OPT_INDENT_2).decode("utf-8")
            )

    def register_diagnostic_change(
        self,
        diagnostic: str,
        state: str,
        from_state: str = DiagnosticState.unknown,
        reason: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        ts: Optional[datetime.datetime] = None,
    ):
        """
        Save diagnostic state changes to Archive.
        1. Send data to BI Model
        2. Register MX Message
        3. Register object notification
        :param diagnostic: - Diagnostic name
        :param state: Current state
        :param from_state: Previous State
        :param data: Checked data
        :param reason:
        :param ts:
        :return:
        """
        from noc.core.service.loader import get_service
        from noc.core.mx import DEFAULT_ENCODING, MessageType

        if self.dry_run:
            self.logger.info(
                "[%s] Register change: %s -> %s",
                diagnostic,
                state,
                from_state,
            )
            return
        svc = get_service()
        if isinstance(ts, str):
            ts = datetime.datetime.fromisoformat(ts)
        now = ts or datetime.datetime.now()
        # Send Data
        dd = {
            "date": now.date().isoformat(),
            "ts": now.replace(microsecond=0).isoformat(sep=" "),
            "managed_object": self.__object.bi_id,
            "diagnostic_name": diagnostic,
            "state": state,
            "from_state": from_state,
        }
        if reason:
            dd["reason"] = reason
        if data:
            dd["data"] = orjson.dumps(data).decode(DEFAULT_ENCODING)
        svc.register_metrics("diagnostichistory", [dd], key=self.__object.bi_id)
        # Send Stream
        # ? always send (from policy)
        if config.message.enable_diagnostic_change:
            run_sync(
                partial(
                    svc.send_message,
                    {
                        "name": diagnostic,
                        "state": state,
                        "from_state": from_state,
                        "reason": reason,
                        "managed_object": self.__object.get_message_context(),
                    },
                    MessageType.DIAGNOSTIC_CHANGE,
                    self.__object.get_mx_message_headers(),
                )
            )
        # Send Notification

    def register_diagnostic_metrics(self, metrics: List[MetricValue]):
        """
        Metrics Labels:
          noc::diagnostic::<name>
          noc::check::<name>
          arg0
        :param metrics:
        :return:
        """
        from noc.core.service.loader import get_service
        from noc.pm.models.metrictype import MetricType

        self.logger.debug("Register diagnostic metrics: %s", metrics)
        svc = get_service()
        r = {}
        now = datetime.datetime.now()
        # Group Metric by row
        for m in metrics:
            mt = MetricType.get_by_name(m.metric_type)
            if not mt:
                self.logger.warning("Unknown MetricType: %s", m.metric_type)
                continue
            if mt.scope.table_name not in r:
                r[mt.scope.table_name] = {}
            key = tuple(m.labels or [])
            if key not in r[mt.scope.table_name]:
                r[mt.scope.table_name][key] = {
                    "date": now.date().isoformat(),
                    "ts": now.replace(microsecond=0).isoformat(sep=" "),
                    "managed_object": self.__object.bi_id,
                    "labels": m.labels,
                    mt.field_name: m.value,
                }
                continue
            r[mt.scope.table_name][key][mt.field_name] = m.value
        for table, data in r.items():
            svc.register_metrics(table, list(data.values()), key=self.__object.bi_id)

    def sync_diagnostic_data(self):
        """Synchronize object data with diagnostic"""


def diagnostic(cls):
    """
    Diagnostic decorator.
     If model supported diagnostic (diagnostics field) add DiagnosticHub
    :param cls:
    :return:
    """

    def diagnostic(self) -> "DiagnosticHub":
        diagnostics = getattr(self, "_diagnostics", None)
        if diagnostics:
            return diagnostics
        self._diagnostics = DiagnosticHub(self)
        return self._diagnostics

    cls.diagnostic = property(diagnostic)
    return cls
