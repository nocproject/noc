# ---------------------------------------------------------------------
# Rule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass

# NOC modules
from noc.core.fm.event import Event
from noc.core.matcher import build_matcher
from noc.fm.models.eventclass import EventClass
from noc.fm.models.alarmclass import AlarmClass
from noc.services.datastream.models.cfgalarm import DispositionRule


@dataclass
class EventAlarmRule:
    name: str
    alarm_class: AlarmClass
    event_class: EventClass
    action: str
    unique: bool
    var_mapping: Dict[str, Any]
    managed_object: str = "managed_object"
    match: Optional[Callable] = None
    match_vars: Optional[Callable] = None
    object_avail_condition: Optional[str] = None
    combo_condition: Optional[str] = None
    combo_window: int = 0
    combo_count: int = 0
    combo_event_classes: List[str] = None
    stop_disposition: bool = False

    @property
    def has_avail_condition(self) -> bool:
        return self.object_avail_condition is not None

    @classmethod
    def from_config(
        cls,
        rule: DispositionRule,
        alarm_class: AlarmClass,
        event_class: Optional[EventClass] = None,
    ) -> "EventAlarmRule":
        """"""
        a_vars = {v.name for v in alarm_class.vars}
        if event_class:
            e_vars = {v.name for v in event_class.vars}
            var_mapping = {v: v for v in a_vars.intersection(e_vars)}
        else:
            var_mapping = {v: v for v in a_vars}
        r = EventAlarmRule(
            name=rule.name,
            alarm_class=alarm_class,
            event_class=event_class,
            action=rule.action,
            unique=alarm_class.is_unique,
            stop_disposition=rule.stop_processing,
            combo_condition="none",
            var_mapping=var_mapping,
        )
        if rule.combo_condition:
            r.combo_condition = rule.combo_condition.combo_condition
            r.combo_window = rule.combo_condition.combo_window
            r.combo_count = rule.combo_condition.combo_count
            r.combo_event_classes = rule.combo_condition.combo_event_classes
        if rule.vars_match_expr:
            r.match_vars = build_matcher(rule.vars_match_expr)
        if rule.match_expr:
            r.match = build_matcher(rule.match_expr)
        if rule.object_avail_condition is not None:
            r.object_avail_condition = rule.object_avail_condition
        return r

    def is_match(self, ctx: Dict[str, Any]) -> bool:
        if self.match and not self.match(ctx):
            return False
        return True

    def is_vars(self, r_vars: Dict[str, Any]) -> bool:
        if self.match_vars and not self.match_vars(r_vars):
            return False
        return True

    def match_event(self, e: Event) -> bool:
        if self.match_vars and not self.match_vars(e.vars):
            return False
        return True

    def get_vars(self, e_vars: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.var_mapping:
            return None
        r = {}
        # Map vars
        for k, v in self.var_mapping.items():
            try:
                r[v] = e_vars[k]
            except KeyError:
                pass
        return r
