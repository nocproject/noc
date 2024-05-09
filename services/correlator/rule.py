# ---------------------------------------------------------------------
# Rule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any, Optional, Dict, List, Set

# NOC modules
from noc.core.fm.event import Event
from noc.fm.models.eventclass import EventClass, EventDispositionRule
from noc.fm.models.activealarm import ComponentHub
from noc.fm.models.alarmclass import AlarmClass


class Rule(object):
    def __init__(self, ec: "EventClass", dr: "EventDispositionRule"):
        self.name: str = dr.name
        self.event_class: "EventClass" = ec
        self.u_name: str = "%s: %s" % (self.event_class.name, self.name)
        self.condition = compile(dr.condition, "<string>", "eval")
        mo_exp = dr.managed_object or "managed_object"
        self.managed_object = compile(mo_exp, "<string>", "eval")
        self.action: str = dr.action
        self.alarm_class: "AlarmClass" = dr.alarm_class
        self.stop_disposition: bool = dr.stop_disposition
        self.var_mapping: Dict[str, Any] = {}  # Map Event to Alarm vars
        self.reference: List[str] = []
        self.c_defaults: Dict[str, Any] = {}  # Static AlarmClass variables
        self.d_defaults: Dict[str, Any] = {}  # Dynamic AlarmClass variables
        if self.alarm_class:
            self.unique: bool = self.alarm_class.is_unique
            a_vars: Set[str] = {v.name for v in self.alarm_class.vars}
            e_vars: Set[str] = {v.name for v in self.event_class.vars}
            for v in a_vars.intersection(e_vars):
                self.var_mapping[v] = v
            if dr.var_mapping:
                self.var_mapping.update(dr.var_mapping)
            self.reference: List[str] = self.alarm_class.reference
            self.combo_condition: str = dr.combo_condition
            self.combo_window: int = dr.combo_window
            self.combo_event_classes: List[str] = [c.id for c in dr.combo_event_classes]
            self.combo_count: int = dr.combo_count
            # Default variables
            for v in self.alarm_class.vars:
                if v.default:
                    if v.default.startswith("="):
                        # Expression
                        # Check component '=component.<name>'
                        _, c_name, *_ = v.default[1:].split(".", 2)
                        self.d_defaults[v.name] = compile(
                            f'{v.default[1:]} if "{c_name}" in components else None',
                            "<string>",
                            "eval",
                        )
                    else:
                        # Constant
                        self.c_defaults[v.name] = v.default

    def get_vars(self, event: "Event", managed_object=None) -> Optional[Dict[str, Any]]:
        """
        Get alarm variables from event.

        :param event: Event
        :param managed_object:
        :returns: Dict of variables or None
        """
        if not self.var_mapping:
            return None
        vars = self.c_defaults.copy()
        # Map vars
        for k, v in self.var_mapping.items():
            try:
                vars[v] = event.vars[k]
            except KeyError:
                pass
        if not self.d_defaults:
            return vars
        # Calculate dynamic defaults
        context = {"components": ComponentHub(self.alarm_class, managed_object, vars.copy())}
        for k, v in self.d_defaults.items():
            x = eval(v, {}, context)
            if x:
                vars[k] = str(x)
        return vars
