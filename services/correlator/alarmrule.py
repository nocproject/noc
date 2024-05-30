# ---------------------------------------------------------------------
# Alarm Rule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
from typing import Optional, DefaultDict, Set, List, Iterable, Pattern, Tuple
from dataclasses import dataclass

# Third-party modules
from jinja2 import Template

# NOC modules
from noc.fm.models.alarmrule import AlarmRule as CfgAlarmRule
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.escalationprofile import EscalationProfile
from noc.main.models.notificationgroup import NotificationGroup

DEFAULT_GROUP_CLASS = "Group"


@dataclass
class Match(object):
    labels: Set[str]
    exclude_labels: Optional[Set[str]]
    alarm_class: Optional[AlarmClass]
    severity: Optional[AlarmSeverity]
    reference_rx: Optional[Pattern]


@dataclass
class Group(object):
    reference_template: Template
    alarm_class: AlarmClass
    title_template: Template
    labels: Optional[List[str]] = None
    min_threshold: int = 0
    max_threshold: int = 0
    window: int = 0


@dataclass
class Action(object):
    policy: str
    notification_group: Optional[NotificationGroup] = None
    escalation_profile: Optional[EscalationProfile] = None
    severity_policy: str = "shift"
    severity: int = 0
    # Sync collection Default ?
    alarm_class: Optional[AlarmClass] = None


@dataclass
class GroupItem(object):
    reference: str
    alarm_class: AlarmClass
    title: str
    labels: Optional[List[str]] = None
    min_threshold: int = 0
    max_threshold: int = 0
    window: int = 0


@dataclass
class ActionItem(object):
    severity: Optional[int] = None
    notification_group: Optional[int] = None
    escalation_profile: Optional[str] = None


class AlarmRule(object):
    _default_alarm_class: Optional[AlarmClass] = None
    severity_policy: str = "AL"

    def __init__(self):
        self.match: List[Match] = []
        self.groups: List[Group] = []
        self.actions: List[Action] = []

    @classmethod
    def try_from(cls, rule_cfg: CfgAlarmRule) -> Optional["AlarmRule"]:
        """
        Generate rule from config
        """
        rule = AlarmRule()
        rule.severity_policy = rule_cfg.severity_policy
        # Add matches
        for match in rule_cfg.match:
            rule.match.append(
                Match(
                    labels=set(match.labels),
                    alarm_class=match.alarm_class,
                    severity=match.severity,
                    exclude_labels=set(match.exclude_labels) if match.exclude_labels else None,
                    reference_rx=re.compile(match.reference_rx) if match.reference_rx else None,
                )
            )
        # Add groups
        for group in rule_cfg.groups:
            rule.groups.append(
                Group(
                    reference_template=Template(group.reference_template),
                    alarm_class=(
                        group.alarm_class if group.alarm_class else cls.get_default_alarm_class()
                    ),
                    title_template=Template(group.title_template),
                    min_threshold=group.min_threshold or 0,
                    max_threshold=group.max_threshold or 0,
                    window=group.window or 0,
                    labels=group.labels or [],
                )
            )
        # Add actions
        for action in rule_cfg.actions:
            if action.when != "raise":
                continue
            rule.actions.append(
                Action(
                    policy=action.policy,
                    notification_group=action.notification_group,
                    escalation_profile=action.escalation,
                    severity=action.min_severity.severity if action.min_severity else None,
                )
            )
        return rule

    def is_match(self, alarm: ActiveAlarm) -> bool:
        """
        Check if alarm matches the rule
        """
        if not self.match:
            return True
        lset = set(alarm.effective_labels)
        for match in self.match:
            # Match against labels
            if match.exclude_labels and match.exclude_labels.issubset(lset):
                continue
            if not match.labels.issubset(lset):
                continue
            # Match against alarm class
            if match.alarm_class and match.alarm_class != alarm.alarm_class:
                continue
            # Match severity
            if match.severity and match.severity != AlarmSeverity.get_severity(alarm.severity):
                continue
            # Match against reference re
            if (
                getattr(alarm, "raw_reference", None)
                and match.reference_rx
                and not match.reference_rx.search(alarm.raw_reference)
            ):
                continue
            return True
        return False

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

    def iter_actions(self, alarm: ActiveAlarm) -> Iterable[Action]:
        """
        Render Group Item
        :param alarm:
        :return:
        """
        for action in self.actions:
            yield action


class AlarmRuleSet(object):
    """
    Full set of alarm rules
    """

    def __init__(self):
        self._label_rules: DefaultDict[Tuple[str, ...], List[AlarmRule]] = defaultdict(list)
        self.label_rules: List[Tuple[Set[str], List[AlarmRule]]] = []

    def add(self, rule: CfgAlarmRule):
        """
        Add rule to set
        """
        if not rule.is_active:
            return
        new_rule = AlarmRule.try_from(rule)
        if not new_rule:
            return
        if rule.match:
            for match in rule.match:
                lset = tuple(sorted(match.labels))
                self._label_rules[lset].append(new_rule)
        else:
            self._label_rules[tuple()].append(new_rule)

    def compile(self):
        """
        Finalize rules
        """
        self.label_rules = [(set(k), v) for k, v in self._label_rules.items()]
        self._label_rules = defaultdict(list)

    def iter_candidates(self, alarm: ActiveAlarm) -> Iterable[AlarmRule]:
        """
        Iterable candidate rules with matching labels
        """
        lset = set(alarm.effective_labels)
        seen: Set[AlarmRule] = set()
        for mset, rules in self.label_rules:
            if not mset.issubset(lset):
                continue
            for rule in rules:
                if rule in seen:
                    continue
                yield rule
                seen.add(rule)

    def iter_rules(self, alarm: ActiveAlarm) -> Iterable[AlarmRule]:
        """
        Iterate all matched rules
        """
        for rule in self.iter_candidates(alarm):
            if rule.is_match(alarm):
                yield rule
