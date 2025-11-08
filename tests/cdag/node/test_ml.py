# ----------------------------------------------------------------------
# Test ML functions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .util import NodeCDAG


@pytest.mark.parametrize(
    ("op", "config", "measures", "expected"),
    [
        # gauss
        (
            "gauss",
            {"min_window": 3},
            [1.0, 1.0, 1.0, 1.0, 0.2, 1.0],
            [1.0, 1.0, 1.0, 1.0, 0.0, 1.0],
        ),
        (
            "gauss",
            {"min_window": 3, "true_level": 0.0, "false_level": 1.0},
            [1.0, 1.0, 1.0, 1.0, 0.2, 1.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        ),
        (
            "gauss",
            {"min_window": 3},
            [1.0, 1.1, 0.9, 1.1, 0.2, 1.0],
            [1.0, 1.0, 1.0, 1.0, 0.0, 1.0],
        ),
    ],
)
def test_ml_node(op, config, measures, expected):
    state = {}
    cdag = NodeCDAG(op, config=config, state=state)
    for ms, exp in zip(measures, expected):
        cdag.begin()
        cdag.activate("x", ms)
        value = cdag.get_value()
        if exp is None:
            assert value is exp
        else:
            assert value == pytest.approx(exp)
