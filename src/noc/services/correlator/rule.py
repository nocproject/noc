# ---------------------------------------------------------------------
# Rule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any
from collections.abc import Callable
from dataclasses import dataclass

# NOC modules
from noc.core.fm.event import Event
from noc.core.matcher import build_matcher
from noc.core.models.valuetype import ValueType
from noc.fm.models.eventclass import EventClass
from noc.fm.models.alarmclass import AlarmClass
from noc.services.datastream.models.cfgalarm import DispositionRule
from noc.models import get_model


@dataclass
class VarTransformRule:
    """Transform variables by rule"""

    name: str
    wildcard: str | None = None
    required: bool = False
    affected_model: Any | None = None
    alias: str | None = None
    value_type: ValueType | None = None
    update_oper_status: bool = False

    @classmethod
    def from_item(cls, item, alias: str | None = None) -> "VarTransformRule":
        """Create var transform rule from config item"""
        if item.affected_model:
            model = get_model(item.affected_model)
            # hasattr component
        else:
            model = None
        return VarTransformRule(
            name=item.name,
            wildcard=item.wildcard or None,
            required=item.required,
            affected_model=model,
            alias=alias or item.alias,
            value_type=item.value_type or None,
            update_oper_status=item.update_oper_status,
        )

    def transform(self, v: dict[str, Any], var_ctx: dict[str, Any]):
        """Transform vars"""
        if self.value_type:
            v[self.name] = self.value_type.clean_value(v[self.name])


@dataclass
class EventAlarmRule:
    name: str
    alarm_class: AlarmClass | None
    event_class: EventClass | None
    action: str
    unique: bool
    vars_transform: list[VarTransformRule]
    # component
    managed_object: str = "managed_object"
    match: Callable | None = None
    match_vars: Callable | None = None
    object_avail_condition: str | None = None
    combo_condition: str | None = None
    combo_window: int = 0
    combo_count: int = 0
    combo_event_classes: list[str] | None = None
    preference: int = 999
    reference_lookup: bool = False
    stop_disposition: bool = False
    condition: str | None = None

    @property
    def has_avail_condition(self) -> bool:
        return self.object_avail_condition is not None

    @classmethod
    def from_config(
        cls,
        rule: DispositionRule,
        alarm_class: AlarmClass,
        event_class: EventClass | None = None,
    ) -> "EventAlarmRule":
        """"""
        a_vars = {v.name: v for v in alarm_class.vars}
        vars_transform = []
        for t in rule.vars_transform:
            vars_transform.append(VarTransformRule.from_item(t))
            if t.name in a_vars:
                a_vars.pop(t.name)
        for v in a_vars:
            vars_transform.append(VarTransformRule(name=v))
        # ctx_transforms
        r = EventAlarmRule(
            name=rule.name,
            alarm_class=alarm_class,
            event_class=event_class,
            action=rule.action,
            unique=alarm_class.is_unique,
            stop_disposition=rule.stop_processing,
            combo_condition="none",
            preference=rule.preference,
            vars_transform=vars_transform,
        )
        if rule.reference_lookup:
            r.reference_lookup = rule.reference_lookup
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

    @classmethod
    def from_event_class_rule(
        cls, source, alarm_class: AlarmClass | None, event_class: EventClass
    ) -> "EventAlarmRule":
        """Restore disposition rules embedded in EventClass."""
        var_mapping = source.var_mapping or {}
        mapped_vars = set(var_mapping.values())
        vars_transform = [
            VarTransformRule(name=target, alias=source_name)
            for source_name, target in var_mapping.items()
        ]
        if alarm_class:
            vars_transform.extend(
                VarTransformRule(name=v.name) for v in alarm_class.vars if v.name not in mapped_vars
            )
        return cls(
            name=f"{event_class.name}: {source.name}",
            alarm_class=alarm_class,
            event_class=event_class,
            action=source.action,
            unique=alarm_class.is_unique if alarm_class else False,
            vars_transform=vars_transform,
            managed_object=source.managed_object or "managed_object",
            combo_condition=source.combo_condition,
            combo_window=source.combo_window,
            combo_count=source.combo_count,
            combo_event_classes=[ec.name for ec in source.combo_event_classes],
            stop_disposition=source.stop_disposition,
            condition=source.condition,
        )

    def is_match(self, ctx: dict[str, Any]) -> bool:
        return not (self.match and not self.match(ctx))

    def is_vars(self, r_vars: dict[str, Any]) -> bool:
        return not (self.match_vars and not self.match_vars(r_vars))

    def match_event(self, e: Event) -> bool:
        return not (self.match_vars and not self.match_vars(e.vars))

    def get_vars(self, e_vars: dict[str, Any]) -> dict[str, Any] | None:
        if not self.vars_transform:
            return None
        ctx: dict[str, Any] = {}
        # Transform
        for k in self.vars_transform:
            if k.name in e_vars:
                v = e_vars[k.name]
            elif k.alias and k.alias in e_vars:
                v = e_vars[k.alias]
            elif ctx and k.name in ctx:
                v = ctx[k.name]
            elif ctx and ctx.get(k.alias):
                v = ctx[k.alias]
            elif k.required:
                raise ValueError(f"Not exists required var: {k.name}")
            else:
                continue
            if k.value_type:
                v = k.value_type.clean_value(v)
            if k.affected_model:
                v = k.affected_model.get_component(**ctx)
                if v:
                    v = str(v.id)
            ctx[k.name] = v
            # if k.name in alamr_vars:
            #     r[k.name] = v
            # Filter Ctx by Alarm vars
        return ctx
