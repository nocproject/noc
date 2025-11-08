# ----------------------------------------------------------------------
# Test WindowNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .util import NodeCDAG

# Sequence of zeroes
SEQ_CONST1 = [1.0] * 10

# Raising sequence
SEQ_RAISE = [float(x) for x in range(10)]

# Normally-distributed sequence, mean = 0, stddev = 1
SEQ_NORMAL_0_1 = [
    -0.31667326,
    -0.87721182,
    -0.83043279,
    -0.81952572,
    -0.92895333,
    0.06855883,
    1.78234451,
    -0.27726999,
    -1.28298013,
    1.78965136,
    -1.43366771,
    1.51864842,
    -0.77011192,
    0.92070883,
    0.55713896,
    -0.64985984,
    0.02078904,
    1.32513769,
    -0.81587468,
    -0.113403,
]


@pytest.mark.parametrize(
    ("op", "config", "measures", "expected"),
    [
        # mean
        ("mean", {}, SEQ_CONST1, [None, None, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
        (
            "mean",
            {},
            SEQ_RAISE,
            [None, None, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5],
        ),
        (
            "mean",
            {"min_window": 5},
            SEQ_RAISE,
            [None, None, None, None, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5],
        ),
        (
            "mean",
            {"min_window": 1, "max_window": 2},
            SEQ_RAISE,
            [0.0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5],
        ),
        (
            "mean",
            {},
            SEQ_NORMAL_0_1,
            [
                None,
                None,
                -0.6747726216863974,
                -0.7109608957054698,
                -0.7545593821708785,
                -0.617373013251503,
                -0.27455622387958795,
                -0.27489544509649017,
                -0.3869048549695963,
            ],
        ),
        # std
        ("std", {}, SEQ_CONST1, [None, None, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        (
            "std",
            {},
            SEQ_NORMAL_0_1,
            [
                None,
                None,
                0.25393363296570126,
                0.22867114165293165,
                0.22234141521598452,
                0.36782729638227385,
                0.9061505915892097,
                0.8476267387841144,
                0.8596568091763175,
            ],
        ),
    ],
)
def test_statistic_node(op, config, measures, expected):
    state = {}
    cdag = NodeCDAG(op, config=config, state=state)
    for ms, exp in zip(measures, expected):
        cdag.begin()
        cdag.activate("x", ms)
        value = cdag.get_value()
        if exp is None:
            assert value is None
        else:
            assert value == pytest.approx(exp)
