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


@dataclass
class EventAlarmRule:
    name: str
    alarm_class: AlarmClass
    event_class: EventClass
    action: str
    unique: bool
    var_mapping: Dict[str, Any]
    match: Optional[Callable] = None
    match_vars: Optional[Callable] = None
    combo_condition: Optional[str] = None
    combo_window: int = 0
    combo_count: int = 0
    combo_event_classes: List[str] = None
    stop_disposition: bool = False

    @classmethod
    def from_config(cls, data, event_class: EventClass) -> "EventAlarmRule":
        """"""
        alarm_class = AlarmClass.get_by_name(data["alarm_class"])
        a_vars = {v.name for v in alarm_class.vars}
        e_vars = {v.name for v in event_class.vars}
        r = EventAlarmRule(
            name=data["name"],
            alarm_class=alarm_class,
            event_class=event_class,
            action=data["action"],
            unique=alarm_class.is_unique,
            stop_disposition=data["stop_processing"],
            var_mapping={v: v for v in a_vars.intersection(e_vars)},
        )
        if "combo_condition" in data:
            r.combo_condition = data["combo_condition"]["combo_condition"]
            r.combo_window = data["combo_condition"]["combo_window"]
            r.combo_count = data["combo_condition"]["combo_count"]
            r.combo_event_classes = data["combo_condition"]["combo_event_classes"]
        if data["vars_match_expr"]:
            r.match_vars = build_matcher(data["vars_match_expr"])
        return r

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
