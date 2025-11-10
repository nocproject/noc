# ----------------------------------------------------------------------
# EscalationPolicy tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Iterable, List

# Third-party modules
import pytest

# NOC modules
from noc.core.models.escalationpolicy import EscalationPolicy


def test_default():
    assert EscalationPolicy.get_default() == EscalationPolicy.ROOT


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("xxx", None),
        ("noc::escalation::never", EscalationPolicy.NEVER),
        ("noc::escalation::rootfirst", EscalationPolicy.ROOT_FIRST),
        ("noc::escalation::root", EscalationPolicy.ROOT),
        ("noc::escalation::alwaysfirst", EscalationPolicy.ALWAYS_FIRST),
        ("noc::escalation::always", EscalationPolicy.ALWAYS),
    ],
)
def test_try_from_label(label: str, expected: Optional[EscalationPolicy]):
    assert EscalationPolicy.try_from_label(label) is expected


@pytest.mark.parametrize(
    ("labels", "expected"),
    [
        # Empty leads to defaults
        ([], EscalationPolicy.ROOT),
        # Missed leads to defaults
        ([["lorem", "ipsum"], ["dorem", "sit", "amet"]], EscalationPolicy.ROOT),
        # Single match
        (
            [["lorem", "noc::escalation::always", "ipsum"], ["dorem", "sit", "amet"]],
            EscalationPolicy.ALWAYS,
        ),
        (
            [["lorem", "noc::escalation::alwaysfirst", "ipsum"], ["dorem", "sit", "amet"]],
            EscalationPolicy.ALWAYS_FIRST,
        ),
        (
            [["lorem", "ipsum"], ["dorem", "noc::escalation::alwaysfirst", "sit", "amet"]],
            EscalationPolicy.ALWAYS_FIRST,
        ),
        # Multiple
        (
            [["lorem", "ipsum"], ["dorem", "noc::escalation::alwaysfirst", "sit", "amet"]],
            EscalationPolicy.ALWAYS_FIRST,
        ),
        (
            [
                ["lorem", "noc::escalation::rootfirst", "ipsum"],
                ["dorem", "noc::escalation::alwaysfirst", "sit", "amet"],
            ],
            EscalationPolicy.ROOT_FIRST,
        ),
        (
            [
                ["lorem", "noc::escalation::alwaysfirst", "ipsum"],
                ["dorem", "noc::escalation::rootfirst", "sit", "amet"],
            ],
            EscalationPolicy.ROOT_FIRST,
        ),
    ],
)
def test_get_effective_policy(labels: Iterable[List[str]], expected: EscalationPolicy):
    assert EscalationPolicy.get_effective_policy(labels) is expected
