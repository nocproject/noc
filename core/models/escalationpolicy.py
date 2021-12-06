# ----------------------------------------------------------------------
# EscalationPolicy enum
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from enum import Enum
from typing import Optional, Iterable, List, Tuple


class EscalationPolicy(Enum):
    # Never escalate
    NEVER = 0
    # Escalate only first root cause in group
    ROOT_FIRST = 1
    # Escalate only root causes
    ROOT = 2
    # Escalate any first alarm in the group,
    # prefer root causes
    ALWAYS_FIRST = 3
    # Always escalate
    ALWAYS = 4

    @classmethod
    def try_from_label(cls, label: str) -> Optional["EscalationPolicy"]:
        """
        Convert label to EscalationPolicy instance
        """
        return _LABEL_TO_POLICY.get(label)

    @classmethod
    def try_from_choice(cls, choice: str) -> Optional["EscalationPolicy"]:
        """
        Convert model value to EscalationPolicy instance
        """
        return _LABEL_TO_POLICY.get(f"noc::escalation::{choice}")

    @classmethod
    def get_default(cls) -> "EscalationPolicy":
        """
        Get default escalation policy
        """
        return EscalationPolicy.ROOT

    @classmethod
    def get_effective_policy(cls, labels: Iterable[List[str]]) -> "EscalationPolicy":
        """
        Calculate effective policy from a sequence of labels
        """
        r: Optional[EscalationPolicy] = None
        for l_set in labels:
            for label in l_set:
                if label.startswith("noc::escalation::"):
                    policy = EscalationPolicy.try_from_label(label)
                    if policy and (not r or r.value > policy.value):
                        r = policy
        if r is None:
            r = EscalationPolicy.get_default()
        return r

    @classmethod
    def get_choices(cls) -> List[Tuple[str, str]]:
        """
        Get `choices` for mongo/django models
        """
        return [(k.split("::")[-1], _LABEL_TO_POLICY[k].name) for k in _LABEL_TO_POLICY]


_LABEL_TO_POLICY = {
    "noc::escalation::never": EscalationPolicy.NEVER,
    "noc::escalation::rootfirst": EscalationPolicy.ROOT_FIRST,
    "noc::escalation::root": EscalationPolicy.ROOT,
    "noc::escalation::alwaysfirst": EscalationPolicy.ALWAYS_FIRST,
    "noc::escalation::always": EscalationPolicy.ALWAYS,
}
