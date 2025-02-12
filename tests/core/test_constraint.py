# ----------------------------------------------------------------------
# TechDomain tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable

# Third-party modules
import pytest

# NOC modules
from noc.core.constraint.base import BaseConstraint
from noc.core.constraint.constraintset import ConstraintSet
from noc.core.constraint.protocol import ProtocolConstraint
from noc.core.constraint.wave import LambdaConstraint


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (ProtocolConstraint("ODU2"), ProtocolConstraint("ODUC2"), False),
        (ProtocolConstraint("ODU4"), ProtocolConstraint("ODU4"), True),
        (LambdaConstraint(1000, 10), LambdaConstraint(1050, 10), False),
        (LambdaConstraint(1000, 10), LambdaConstraint(1000, 10), True),
    ],
)
def test_constraint_satisfy(left: BaseConstraint, right: BaseConstraint, expected: bool) -> None:
    r = left.satisfy(right)
    assert r == expected


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ([], [], []),
        ([ProtocolConstraint("ODU2")], [ProtocolConstraint("ODU4")], None),
        ([ProtocolConstraint("ODU4")], [ProtocolConstraint("ODU4")], [ProtocolConstraint("ODU4")]),
        (
            [ProtocolConstraint("ODU2"), ProtocolConstraint("ODU4")],
            [ProtocolConstraint("ODU4")],
            [ProtocolConstraint("ODU4")],
        ),
    ],
)
def test_constraint_set_intersect(
    left: Iterable[BaseConstraint],
    right: Iterable[BaseConstraint],
    expected: Iterable[BaseConstraint] | None,
) -> None:
    x = ConstraintSet.from_iter(left)
    y = ConstraintSet.from_iter(right)
    r = x.intersect(y)
    if expected is None:
        assert r is None
    else:
        assert r is not None
        assert list(r) == list(expected)


@pytest.mark.parametrize(("x", "expected"), [("lambda::192100-50", "C21 (50 GHz)")])
def test_humanized(x: LambdaConstraint | str, expected: str) -> None:
    if isinstance(x, str):
        x = LambdaConstraint.from_discriminator(x)
    assert x.humanized == expected
