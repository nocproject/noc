# ---------------------------------------------------------------------
# Alarm Rule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional, List, Iterable, Dict, Any, Callable, Tuple

# Third-party modules
from jinja2 import Template

# NOC modules
from noc.core.matcher import build_matcher
from noc.core.fm.request import ActionConfig
from noc.fm.models.alarmrule import AlarmRule as CfgAlarmRule
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.escalationprofile import EscalationProfile


DEFAULT_GROUP_CLASS = "Group"


@dataclass
class Group(object):
    reference_template: Template
    alarm_class: AlarmClass
    title_template: Template
    labels: Optional[List[str]] = None
    min_threshold: int = 0
    max_threshold: int = 0
    window: int = 0

    @classmethod
    def from_config(cls, cfg) -> "Group":
        return Group(
            reference_template=Template(cfg["reference_template"]),
            alarm_class=AlarmClass.get_by_id(cfg["alarm_class"]) if cfg["alarm_class"] else None,
            title_template=Template(cfg["title_template"]),
            min_threshold=int(cfg["min_threshold"]),
            max_threshold=int(cfg["max_threshold"]),
            window=int(cfg["window"]),
            labels=cfg["labels"],
        )


@dataclass
class GroupItem(object):
    reference: str
    alarm_class: AlarmClass
    title: str
    labels: Optional[List[str]] = None
    min_threshold: int = 0
    max_threshold: int = 0
    window: int = 0


class AlarmRule(object):
    _default_alarm_class: Optional[AlarmClass] = None
    severity_policy: str = "AL"
    min_severity: Optional[int] = None
    max_severity: Optional[int] = None
    escalation_profile: Optional[EscalationProfile] = None

    def __init__(self, name):
        self.name = name
        self.matcher: Optional[Callable] = None
        self.groups: List[Group] = []
        self.actions: List[ActionConfig] = []
        self.severity_match: bool = True

    def get_severity(self, alarm: ActiveAlarm) -> int:
        # Calculate only one per policy
        severity = alarm.get_effective_severity(policy=self.severity_policy)
        if self.min_severity:
            severity = max(severity, self.min_severity)
        if self.max_severity:
            severity = min(severity, self.max_severity)
        return severity

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "AlarmRule":
        """Generate rule from config"""
        rule = AlarmRule(name=config["name"])
        if config["match_expr"]:
            rule.matcher = cls.get_matcher(config["match_expr"])
        for g in config["groups"]:
            g = Group.from_config(g)
            g.alarm_class = g.alarm_class or cls.get_default_alarm_class()
            rule.groups.append(g)
        for a in config["actions"]:
            rule.actions += [ActionConfig.model_validate(a)]
        rule.severity_policy = config["severity_policy"]
        return rule

    @classmethod
    def get_matcher(cls, expr: List[Dict[str, Any]]) -> Callable:
        """"""
        if len(expr) == 1:
            return build_matcher(expr[0])
        return build_matcher({"$or": expr})

    def is_match(self, alarm: ActiveAlarm, severity: Optional[int] = None) -> bool:
        """
        Check if alarm matches the rule
        """
        if not self.matcher:
            return True
        ctx = alarm.get_matcher_ctx()
        if self.severity_match and severity:
            ctx["severity"] = severity
        return self.matcher(ctx)

    @classmethod
    def get_default_alarm_class(cls) -> AlarmClass:
        if not cls._default_alarm_class:
            cls._default_alarm_class = AlarmClass.get_by_name(DEFAULT_GROUP_CLASS)
            assert cls._default_alarm_class
        return cls._default_alarm_class

    def iter_groups(self, alarm: ActiveAlarm) -> Iterable[GroupItem]:
        """
        Render group templates
        """
        ctx = {"alarm": alarm}
        for group in self.groups:
            yield GroupItem(
                reference=group.reference_template.render(**ctx),
                alarm_class=group.alarm_class,
                title=group.title_template.render(**ctx),
                labels=group.labels,
                min_threshold=group.min_threshold,
                max_threshold=group.max_threshold,
                window=group.window,
            )

    def iter_actions(self, alarm: ActiveAlarm) -> Iterable[ActionConfig]:
        """Render Group Item"""
        for action in self.actions:
            yield action


class AlarmRuleSet(object):
    """
    Full set of alarm rules
    """

    def __init__(self):
        self.common_rules = []
        self.alarm_class_rules: Dict[str, List[AlarmRule]] = {}

    def add(self, rule: CfgAlarmRule):
        """
        Add rule to set
        """
        if not rule.is_active:
            return
        new_rule = AlarmRule.from_config(CfgAlarmRule.get_config(rule))
        if not new_rule:
            return
        self.common_rules.append(new_rule)

    def iter_candidates(self, alarm: ActiveAlarm) -> Iterable[AlarmRule]:
        """
        Iterable candidate rules with matching labels
        """
        for rule in self.common_rules:
            yield rule

    def iter_rules(self, alarm: ActiveAlarm) -> Iterable[Tuple[AlarmRule, int]]:
        """
        Iterate all matched rules
        """
        for rule in self.iter_candidates(alarm):
            severity = rule.get_severity(alarm)
            if rule.is_match(alarm, severity=severity):
                yield rule, severity
