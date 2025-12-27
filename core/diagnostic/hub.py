# ----------------------------------------------------------------------
# @diagnostic decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
import itertools
from collections import defaultdict
from functools import partial
from typing import Optional, List, Dict, Any, Iterable, Tuple, Set, Union

# Third-party modules
import orjson
from pydantic import BaseModel, PrivateAttr

# NOC modules
from noc.core.ioloop.util import run_sync
from noc.core.checkers.base import Check, CheckResult, MetricValue
from noc.core.handler import get_handler
from noc.config import config
from noc.models import is_document
from .types import DiagnosticConfig, DiagnosticState, CheckStatus, DiagnosticValue
from .handler import DiagnosticHandler

diagnostic_logger = logging.getLogger(__name__)

# BuiltIn Diagnostics
SA_DIAG = "SA"
EVENT_DIAG = "FM_EVENT"
ALARM_DIAG = "FM_ALARM"
TT_DIAG = "TT"
SNMP_DIAG = "SNMP"
PROFILE_DIAG = "Profile"
CLI_DIAG = "CLI"
HTTP_DIAG = "HTTP"
HTTPS_DIAG = "HTTPS"
SYSLOG_DIAG = "SYSLOG"
SNMPTRAP_DIAG = "SNMPTRAP"
FIRST_AVAIL = "FIRST_AVAIL"
RESOLVER_DIAG = "ADDR_RESOLVER"
# SA Diags
SA_DIAGS = {SNMP_DIAG, PROFILE_DIAG, CLI_DIAG, HTTP_DIAG}
FM_DIAGS = {SNMPTRAP_DIAG, SYSLOG_DIAG}
DIAGNOCSTIC_LABEL_SCOPE = "diag"
DEFER_CHANGE_STATE = "noc.core.diagnostic.decorator.change_state"


def json_default(obj):
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if isinstance(obj, datetime.datetime):
        return obj.replace(microsecond=0).isoformat(sep=" ")
    raise TypeError


DIAGNOSTIC_CHECK_STATE: Dict[bool, DiagnosticState] = {
    True: DiagnosticState("enabled"),
    False: DiagnosticState("failed"),
}


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

    def __init__(self, cfg: Optional[DiagnosticConfig] = None, **data):
        super().__init__(**data)
        self._config = cfg

    def __eq__(self, other: Union["DiagnosticItem", "DiagnosticValue"]) -> bool:
        """Compare diagnostic by value"""
        if self.diagnostic != other.diagnostic:
            return False
        return (
            self.state == other.state
            and self.checks == other.checks
            and self.reason == other.reason
            and self.changed == other.changed
        )

    @property
    def config(self):
        return self._config

    @property
    def show_in_display(self) -> bool:
        """Show Diagnostic Value on Display"""
        if (
            self.config.show_in_display
            and self.config.hide_enable
            and self.state == DiagnosticState.enabled
        ):
            return False
        return self.config.show_in_display

    @property
    def workflow_event(self) -> Optional[str]:
        if not self.config.workflow_event:
            return None
        if self.state not in (DiagnosticState.enabled, DiagnosticState.blocked):
            return self.config.workflow_event
        return None

    @property
    def is_active(self) -> bool:
        """
        Check diagnostic has worked: Enabled or Failed state
        """
        return self.state in (DiagnosticState.enabled, DiagnosticState.failed)

    @property
    def is_failed(self) -> bool:
        return self.state == DiagnosticState.failed

    @classmethod
    def from_config(
        cls,
        cfg: DiagnosticConfig,
        value: Optional[DiagnosticValue] = None,
    ) -> "DiagnosticItem":
        """Create item from config"""
        if cfg.blocked:
            state = DiagnosticState.blocked
        elif not value or value.state == DiagnosticState.blocked:
            state = cfg.default_state
        else:
            state = value.state
        return DiagnosticItem(
            cfg=cfg,
            diagnostic=cfg.diagnostic,
            state=state,
            checks=value.checks if value else None,
            reason=cfg.reason or None,
            changed=value.changed if value else None,
        )

    def reset(self, reason="Reset by"):
        if self.config.blocked:
            self.state = DiagnosticState.blocked
            self.reason = self.config.reason
        else:
            self.state = self.config.default_state
            self.reason = reason
        self.checks = []
        self.changed = datetime.datetime.now()

    def get_handler(self, logger=None) -> DiagnosticHandler:
        if not hasattr(self, "_handler"):
            h = get_handler(self.config.diagnostic_handler)
            if not h:
                raise AttributeError("Unknown Diagnostic Handler")
            try:
                self._handler = h(config=self.config, logger=logger)
            except TypeError as e:
                raise AttributeError(str(e))
        return self._handler

    def iter_checks(
        self,
        logger=None,
        **kwargs,
    ) -> Iterable[Tuple[Check, ...]]:
        """Iterate over checks"""
        if not self.config.diagnostic_handler and not self.config.checks:
            return
        elif not self.config.diagnostic_handler:
            yield tuple(self.config.checks)
            return
        h = self.get_handler(logger=logger)
        yield from h.iter_checks(**kwargs)

    def get_check_status(
        self, checks: List[CheckResult]
    ) -> Tuple[Optional[bool], Optional[str], Dict[str, Any], List[CheckStatus]]:
        """
        Calculate check status, ANY or ALL policy apply
        """
        if self.config.diagnostic_handler:
            h = self.get_handler()
            return h.get_result(checks)
        state = None
        data = {}
        to_result = [CheckStatus.from_result(c) for c in checks if not c.skipped]
        for c in checks:
            c = CheckStatus.from_result(c)
            if c.skipped:
                continue
            if not c.status and self.config.state_policy == "ALL":
                state = False
                break
            if c.status and self.config.state_policy == "ANY":
                state = True
                break
        if self.config.state_policy == "ANY" and checks and state is None:
            state = False
        return state, None, data, to_result

    def update_checks(self, checks: List[CheckStatus]) -> bool:
        """Update object checks"""
        status = {c.name: c.status for c in self.checks or []}
        changed = False
        for c in checks:
            if c.name not in status or c.status != status[c.name]:
                changed = True
                break
        if changed:
            self.checks = checks
        return changed

    def get_object_form(self) -> Dict[str, Any]:
        """Displayed form"""
        return {
            "name": self.diagnostic[:6],
            "description": self.config.display_description,
            "state": self.state.value,
            "state__label": self.state.value,
            "details": [
                {
                    "name": c.name,
                    "state": {True: "OK", False: "Error"}[c.status],
                    "error": c.error,
                }
                for c in self.checks or []
                if not c.skipped
            ],
            "reason": self.reason or "",
        }

    def get_value(self) -> DiagnosticValue:
        """"""
        return DiagnosticValue(
            diagnostic=self.diagnostic,
            state=self.state,
            checks=self.checks,
            reason=self.reason or None,
            changed=self.changed,
        )


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
        self.__checks: Optional[Dict[str, Set[str]]] = None
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

    def set_dry_run(self):
        self.dry_run = True

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
        """
        d = self.get(name)
        if d is None:
            return False
        return d.is_active

    def has_failed_diagnostic(self, name: str) -> bool:
        """
        Check diagnostic has worked: Enabled or Failed state
        """
        d = self.get(name)
        if d is None:
            return False
        return d.is_failed

    def get_object_diagnostic_value(self, name: str) -> Optional[DiagnosticValue]:
        """
        Get DiagnosticItem from Object
        Args:
            name: Diagnostic Name
        """
        values = self.__object.get_diagnostic_values()
        return values.get(name)

    def iter_diagnostic_configs(self) -> Iterable[DiagnosticConfig]:
        for d in self:
            yield d.config

    def __load_diagnostics(self):
        """Loading Diagnostic from Object Config"""
        r = {}
        values = self.__object.get_diagnostic_values()
        locals = []
        for cfg in self.__object.iter_diagnostic_configs():
            r[cfg.diagnostic] = DiagnosticItem.from_config(cfg, value=values.get(cfg.diagnostic))
            for dd in cfg.dependent or []:
                self.__depended[dd] = cfg.diagnostic
            if cfg.is_local_status:
                locals.append(cfg)
        self.__diagnostics = r
        for cfg in locals:
            h = self[cfg.diagnostic].get_handler(self.logger)
            ctx = self.get_check_env(self.__object, cfg)
            c_state, c_reason, c_data, c_checks = h.get_check_status(**ctx)
            self.set_state(cfg.diagnostic, c_state, reason=c_reason, data=c_data)

    def __load_checks(self):
        """Loading all diagnostic checks"""
        if self.__diagnostics is None:
            self.__load_diagnostics()
        for d in self.__diagnostics:
            list(self.iter_checks(d))

    @classmethod
    def get_check_env(
        cls, obj, cfg: DiagnosticConfig, checks_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Getting checks environment context"""
        ctx = obj.get_check_ctx(
            include_credentials=cfg.include_credentials,
        )
        checks_data = checks_data or {}
        for ci in cfg.diagnostic_ctx or []:
            if ci.name in checks_data:
                ctx[ci.alias or ci.name] = checks_data[ci.name]
            elif ci.value:
                ctx[ci.alias or ci.name] = ci.value
        return ctx

    def iter_checks(self, name: str) -> Iterable[Tuple[Check, ...]]:
        if self.__checks is None:
            self.__checks = defaultdict(set)
        di = self[name]
        ctx = self.get_check_env(self.__object, di.config, self.__data)
        for checks in di.iter_checks(**ctx, logger=self.logger):
            for c in itertools.chain(checks):
                self.__checks[c.key].add(di.diagnostic)
            yield checks

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
        if data:
            self.apply_context_data(d, data)
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

    def update_checks(self, checks: List[CheckResult], dry_run: bool = False):
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
                            labels=[*m_labels, f"noc::diagnostic::{d}"],
                        )
                    ]
        # Calculate State and Update diagnostic
        for d, crs in affected_diagnostics.items():
            c_state, c_reason, c_data, c_checks = self[d].get_check_status(crs)
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
            changed = self[d].update_checks(c_checks)
            if changed:
                self.sync_diagnostics(dry_run)
        if metrics and not self.dry_run:
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

    def sync_diagnostics(self, dry_run: bool = False):
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
        dry_run |= self.dry_run
        new_diags, changed_states, wf_events = [], set(), set()
        changed = []
        for di_new in self:
            d_name = di_new.diagnostic
            d_current = self.get_object_diagnostic_value(d_name)
            if not d_current:
                new_diags.append(di_new)
                changed.append(d_name)
                continue
            if d_current == di_new and di_new.workflow_event:
                self.logger.debug(
                    "[%s] Send Workflow Event: %s",
                    d_name,
                    di_new.workflow_event,
                )
                wf_events.add(di_new.workflow_event)
            # Compare state
            if d_current.state != di_new.state:
                if d_current.state == DiagnosticState.failed or di_new.is_failed:
                    changed_states.add(d_name)
                changed.append(d_name)
                self.register_diagnostic_change(
                    d_name,
                    state=di_new.state,
                    from_state=d_current.state,
                    reason=di_new.reason,
                    ts=di_new.changed,
                )
                if di_new.state == DiagnosticState.enabled and di_new.config.workflow_enabled_event:
                    wf_events.add(di_new.config.workflow_enabled_event)
            # Save diagnostic with checks value (for update checks)
            elif d_current != di_new:
                self.logger.debug("[%s] Diagnostic Same, next.", d_name)
                changed.append(d_name)
            new_diags.append(di_new)
        if changed:
            self.logger.info(
                "[%s] Save changed diagnostics: %s (DR: %s)", str(self.__object), changed, dry_run
            )
            self.__object.save_diagnostics(new_diags, dry_run=dry_run)
        if wf_events:
            # Bulk update/Get effective event
            self.__object.fire_event(next(iter(wf_events)))
        if changed_states and self.sync_alarm:
            self.sync_alarms(self.__object, new_diags, dry_run=dry_run)

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
            self.logger.debug("Removed diagnostics: %s", list(remove))
            params += remove
            query_set += " - %s" * len(remove)
        if update:
            self.logger.debug("Update diagnostics: %s", [x.diagnostic for x in update])
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

    @classmethod
    def sync_alarms(
        cls,
        o: Any,
        diagnostics: List[DiagnosticItem],
        alarm_disable: bool = False,
        dry_run: bool = False,
    ):
        """
        Raise & clear Alarm for diagnostic. Only diagnostics with alarm_class set will be synced.
        If diagnostics param is set and alarm_class is not set - clear alarm
         For dependent - Group alarm base on diagnostic with alarm for depended
         Args:
            o: object
            diagnostics: If set - sync only params diagnostic and depends
            alarm_disable: Disable alarm by settings. Clear active alarm
            dry_run: Not send ensure event
        """
        from noc.core.service.loader import get_service

        now = datetime.datetime.now()
        # Group Alarms
        groups = {}
        alarms = {}
        alarm_config: Dict[str, Dict[str, Any]] = {}  # diagnostic -> AlarmClass Map
        messages: List[Dict[str, Any]] = []  # Messages for send dispose
        processed = set()
        diagnostics = {d.diagnostic: d for d in diagnostics}
        for d in diagnostics.values():
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
            if dc.dependent:
                groups[dc.diagnostic] = []
                for d_name in dc.dependent:
                    if d_name not in diagnostics:
                        continue
                    dd = diagnostics[d_name]
                    if dd and dd.is_failed and not alarm_disable:
                        groups[dc.diagnostic] += [{"diagnostic": d_name, "reason": dd.reason or ""}]
                    processed.add(d_name)
            elif d and d.state == d.state.failed and not alarm_disable:
                alarms[dc.diagnostic] = {
                    "timestamp": now,
                    "reference": f"dc:{o.id}:{d.diagnostic}",
                    "managed_object": str(o.id),
                    "$op": "raise",
                    "alarm_class": dc.alarm_class,
                    "labels": dc.alarm_labels or [],
                    "vars": {"reason": d.reason or ""},
                }
            else:
                alarms[dc.diagnostic] = {
                    "timestamp": now,
                    "reference": f"dc:{o.id}:{dc.diagnostic}",
                    "$op": "clear",
                }
        # Group Alarm
        for d in groups:
            messages += [
                {
                    "$op": "ensure_group",
                    "reference": f"dc:{d}:{o.id}",
                    "alarm_class": alarm_config[d]["alarm_class"],
                    "alarms": [
                        {
                            "reference": f"dc:{dd['diagnostic']}:{o.id}",
                            "alarm_class": alarm_config[dd["diagnostic"]]["alarm_class"],
                            "managed_object": str(o.id),
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
        if dry_run:
            # self.logger.info("Sync Diagnostic Alarm: %s", messages)
            print(f"Sync Diagnostic Alarm: {messages}")
            return
        # Send Dispose
        svc = get_service()
        for msg in messages:
            stream, partition = o.alarms_stream_and_partition
            svc.publish(
                orjson.dumps(msg),
                stream=stream,
                partition=partition,
            )
            # self.logger.debug(
            #    "Dispose: %s", orjson.dumps(msg, option=orjson.OPT_INDENT_2).decode("utf-8")
            # )

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
        Attrs:
            diagnostic: - Diagnostic name
            state: Current state
            from_state: Previous State
            data: Checked data
            reason:
            ts:
        """
        from noc.core.service.loader import get_service
        from noc.core.mx import DEFAULT_ENCODING, MessageType

        from_state = from_state or DiagnosticState.unknown
        if self.dry_run:
            self.logger.info(
                "[%s] Register change: %s -> %s",
                diagnostic,
                from_state,
                state,
            )
            return
        svc = get_service()
        if isinstance(ts, str):
            ts = datetime.datetime.fromisoformat(ts)
        now = ts or datetime.datetime.now()
        mo = self.__object.get_effective_managed_object()
        # Send Data
        dd = {
            "date": now.date().isoformat(),
            "ts": now.replace(microsecond=0).isoformat(sep=" "),
            "managed_object": mo.bi_id if mo else None,
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
                        "managed_object": mo.get_message_context() if mo else None,
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

    def apply_context_data(self, d: DiagnosticItem, data: Dict[str, Any]):
        self.__data |= data
        if not d.config.diagnostic_ctx:
            return
        for ctx in d.config.diagnostic_ctx:
            if ctx.name in data and ctx.set_method:
                h = getattr(self.__object, ctx.set_method)
                h(data[ctx.name])

    def sync_diagnostic_data(self):
        """Synchronize object data with diagnostic"""


def update_diagnostic_checks(results: Dict[str, Dict[str, Any]]):
    """Update changed Diagnostic statuses"""
    from noc.models import get_model

    diagnostic_logger.info("Update diagnostic statuses: %s", len(results))
    for sid, statuses in results.items():
        obj_type, oid = sid.split(":", 1)
        obj_type = get_model(obj_type)
        if oid.startswith("bi_id"):
            obj = obj_type.get_by_bi_id(int(oid[6:]))
        else:
            obj = obj_type.get_by_id(oid)
        if not obj:
            diagnostic_logger.warning("Unknown Object by OID: %s", oid)
            continue
        statuses = [CheckResult.from_dict(c) for c in statuses]
        try:
            obj.diagnostic.update_checks(statuses)
        except Exception as e:
            diagnostic_logger.error(f"[{obj}] Failed when update diagnostic Statuses: {e}")
            continue
