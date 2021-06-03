# ----------------------------------------------------------------------
# ProbeNode test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .util import NodeCDAG


@pytest.mark.parametrize(
    "unit,data",
    [
        # (unit, [(ts, value, unit, expected, state), ...)
        # Plain measures
        (
            "bit",
            [
                (1621601000_000000000, 1, "bit", 1, None),
                (1621601001_000000000, 2, "bit", 2, None),
                (1621601002_000000000, 3, "bit", 3, None),
            ],
        ),
        # Convert measures
        (
            "bit",
            [
                (1621601000_000000000, 1, "byte", 8, None),
                (1621601001_000000000, 2, "byte", 16, None),
                (1621601002_000000000, 3, "byte", 24, None),
            ],
        ),
        # Mixed measures
        (
            "bit",
            [
                (1621601000_000000000, 1, "bit", 1, None),
                (1621601001_000000000, 2, "byte", 16, None),
                (1621601002_000000000, 3, "bit", 3, None),
            ],
        ),
        # Plain speed
        (
            "bit/s",
            [
                (1621601000_000000000, 1_000, "bit/s", 1_000, None),
                (1621601001_000000000, 2_000, "bit/s", 2_000, None),
                (1621601002_000000000, 3_000, "bit/s", 3_000, None),
            ],
        ),
        # Plain speed
        (
            "bit/s",
            [
                (1621601000_000000000, 1_000, "bit/s", 1_000, None),
                (1621601001_000000000, 2_000, "byte/s", 16_000, None),
                (1621601002_000000000, 3_000, "bit/s", 3_000, None),
            ],
        ),
        # Counter
        (
            "bit/s",
            [
                (
                    1621601000_000000000,
                    1_000,
                    "bit",
                    None,
                    {"lt": 1621601000_000000000, "lv": 1_000},
                ),
                (
                    1621601010_000000000,
                    2_000,
                    "bit",
                    100,
                    {"lt": 1621601010_000000000, "lv": 2_000},
                ),
                (
                    1621601020_000000000,
                    3_500,
                    "bit",
                    150,
                    {"lt": 1621601020_000000000, "lv": 3_500},
                ),
            ],
        ),
        # Counter stepback
        (
            "bit/s",
            [
                (
                    1621601000_000000000,
                    1_000,
                    "bit",
                    None,
                    {"lt": 1621601000_000000000, "lv": 1_000},
                ),
                (
                    1621601010_000000000,
                    2_000,
                    "bit",
                    100,
                    {"lt": 1621601010_000000000, "lv": 2_000},
                ),
                # Time Stepback
                (
                    1621601000_000000000,
                    3_500,
                    "bit",
                    None,
                    None,
                ),
                # Restore
                (
                    1621601030_000000000,
                    5_000,
                    "bit",
                    None,
                    {"lt": 1621601030_000000000, "lv": 5_000},
                ),
                (
                    1621601040_000000000,
                    6_000,
                    "bit",
                    100,
                    {"lt": 1621601040_000000000, "lv": 6_000},
                ),
            ],
        ),
        # Counter + scale
        (
            "bit/s",
            [
                (
                    1621601000_000000000,
                    1_000,
                    "byte",
                    None,
                    {"lt": 1621601000_000000000, "lv": 1_000},
                ),
                (
                    1621601010_000000000,
                    2_000,
                    "byte",
                    800,
                    {"lt": 1621601010_000000000, "lv": 2_000},
                ),
                (
                    1621601020_000000000,
                    3_500,
                    "byte",
                    1200,
                    {"lt": 1621601020_000000000, "lv": 3_500},
                ),
            ],
        ),
        # Counter stepback + scale
        (
            "bit/s",
            [
                (
                    1621601000_000000000,
                    1_000,
                    "byte",
                    None,
                    {"lt": 1621601000_000000000, "lv": 1_000},
                ),
                (
                    1621601010_000000000,
                    2_000,
                    "byte",
                    800,
                    {"lt": 1621601010_000000000, "lv": 2_000},
                ),
                # Time Stepback
                (
                    1621601000_000000000,
                    3_500,
                    "byte",
                    None,
                    None,
                ),
                # Restore
                (
                    1621601030_000000000,
                    5_000,
                    "byte",
                    None,
                    {"lt": 1621601030_000000000, "lv": 5_000},
                ),
                (
                    1621601040_000000000,
                    6_000,
                    "byte",
                    800,
                    {"lt": 1621601040_000000000, "lv": 6_000},
                ),
            ],
        ),
        # Counter wrap, 31 bit
        (
            "bit/s",
            [
                (
                    1621601000_000000000,
                    2147482000,  # MAX31 - 1647
                    "bit",
                    None,
                    {"lt": 1621601000_000000000, "lv": 2147482000},
                ),
                (
                    1621601010_000000000,
                    2147483000,  # MAX31 - 647
                    "bit",
                    100,
                    {"lt": 1621601010_000000000, "lv": 2147483000},
                ),
                # Counter Wrap
                (
                    1621601020_000000000,
                    353,  # 1000 - 647
                    "bit",
                    100,
                    {"lt": 1621601020_000000000, "lv": 353},
                ),
                # Restore
                (
                    1621601030_000000000,
                    1_353,
                    "bit",
                    100,
                    {"lt": 1621601030_000000000, "lv": 1_353},
                ),
            ],
        ),
        # Counter wrap, 32 bit
        (
            "bit/s",
            [
                (
                    1621601000_000000000,
                    4294966000,  # MAX32 - 1295
                    "bit",
                    None,
                    {"lt": 1621601000_000000000, "lv": 4294966000},
                ),
                (
                    1621601010_000000000,
                    4294967000,  # MAX33 - 295
                    "bit",
                    100,
                    {"lt": 1621601010_000000000, "lv": 4294967000},
                ),
                # Counter Wrap
                (
                    1621601020_000000000,
                    705,  # 1000 - 297
                    "bit",
                    100,
                    {"lt": 1621601020_000000000, "lv": 705},
                ),
                # Restore
                (
                    1621601030_000000000,
                    1_705,
                    "bit",
                    100,
                    {"lt": 1621601030_000000000, "lv": 1_705},
                ),
            ],
        ),
        # Counter wrap, 64 bit
        (
            "bit/s",
            [
                (
                    1621601000_000000000,
                    18446744073709550000,  # MAX64 - 1615
                    "bit",
                    None,
                    {"lt": 1621601000_000000000, "lv": 18446744073709550000},
                ),
                (
                    1621601010_000000000,
                    18446744073709551000,  # MAX64 - 615
                    "bit",
                    100,
                    {"lt": 1621601010_000000000, "lv": 18446744073709551000},
                ),
                # Counter Wrap
                (
                    1621601020_000000000,
                    385,  # 1000 - 615
                    "bit",
                    100,
                    {"lt": 1621601020_000000000, "lv": 385},
                ),
                # Restore
                (
                    1621601030_000000000,
                    1_385,
                    "bit",
                    100,
                    {"lt": 1621601030_000000000, "lv": 1_385},
                ),
            ],
        ),
        # Counter stepback, 32 bit
        (
            "bit/s",
            [
                (
                    1621601000_000000000,
                    4294966000,  # MAX32 - 1295
                    "bit",
                    None,
                    {"lt": 1621601000_000000000, "lv": 4294966000},
                ),
                (
                    1621601010_000000000,
                    4294967000,  # MAX33 - 295
                    "bit",
                    100,
                    {"lt": 1621601010_000000000, "lv": 4294967000},
                ),
                # Counter Stepback
                (1621601020_000000000, 4294907000, "bit", None, None),
                # Restore
                (
                    1621601030_000000000,
                    705,
                    "bit",
                    None,
                    {"lt": 1621601030_000000000, "lv": 705},
                ),
                (
                    1621601040_000000000,
                    1_705,
                    "bit",
                    100,
                    {"lt": 1621601040_000000000, "lv": 1_705},
                ),
            ],
        ),
        # Plain measures + scale
        (
            "bit",
            [
                (1621601000_000000000, 1, "k,bit", 1_000, None),
                (1621601001_000000000, 2, "k,bit", 2_000, None),
                (1621601002_000000000, 3, "k,bit", 3_000, None),
            ],
        ),
        # Scaled, plain measures
        (
            "k,bit",
            [
                (1621601000_000000000, 1_000, "bit", 1, None),
                (1621601001_000000000, 2_000, "bit", 2, None),
                (1621601002_000000000, 3_000, "bit", 3, None),
            ],
        ),
        # Scaled, same measures
        (
            "k,bit",
            [
                (1621601000_000000000, 1_000, "k,bit", 1_000, None),
                (1621601001_000000000, 2_000, "k,bit", 2_000, None),
                (1621601002_000000000, 3_000, "k,bit", 3_000, None),
            ],
        ),
        # Scaled, base mismatch
        (
            "bit",
            [
                (1621601000_000000000, 1, "ki,bit", 1_024, None),
                (1621601001_000000000, 2, "ki,bit", 2_048, None),
                (1621601002_000000000, 3, "ki,bit", 3_072, None),
            ],
        ),
        # Scaled, base mismatch
        (
            "ki,bit",
            [
                (1621601000_000000000, 1_024, "bit", 1, None),
                (1621601001_000000000, 2_048, "bit", 2, None),
                (1621601002_000000000, 3_072, "bit", 3, None),
            ],
        ),
        # Full scale mismatch
        (
            "k,bit",
            [
                (1621601000_000000000, 1_000, "ki,bit", 1_024, None),
                (1621601001_000000000, 2_000, "ki,bit", 2_048, None),
                (1621601002_000000000, 3_000, "ki,bit", 3_072, None),
            ],
        ),
    ],
)
def test_probe(unit, data):
    state = {}
    if "," in unit:
        scale, unit = unit.split(",")
    else:
        scale = "1"
    cdag = NodeCDAG("probe", config={"unit": unit, "scale": scale}, state=state)
    for ts, value, m_unit, expected, x_state in data:
        cdag.begin()
        assert cdag.is_activated() is False
        cdag.activate("x", value)
        assert cdag.is_activated() is False
        cdag.activate("ts", ts)
        assert cdag.is_activated() is False
        cdag.activate("unit", m_unit)
        # Should be activated unless None is expected
        x_act = expected is not None
        assert cdag.is_activated() is x_act
        # Check value
        value = cdag.get_value()
        if expected is None:
            assert value is None
        else:
            assert value == expected
        # Check state
        n_state = cdag.get_changed_state()
        if x_state is None:
            assert n_state == {}
        else:
            assert n_state["node"] == x_state


def setup_module(_module):
    from noc.core.cdag.node.probe import ProbeNode

    ProbeNode.set_convert(
        {
            # Name -> alias -> expr
            "bit": {"byte": "x * 8"},
            "bit/s": {
                "byte/s": "x * 8",
                "bit": "delta / time_delta",
                "byte": "delta * 8 / time_delta",
            },
        }
    )
    ProbeNode.set_scale(
        {
            "Y": (10, 24),
            "Z": (10, 21),
            "E": (10, 18),
            "P": (10, 15),
            "T": (10, 12),
            "G": (10, 9),
            "M": (10, 6),
            "k": (10, 3),
            "h": (10, 2),
            "da": (10, 1),
            "1": (10, 0),
            "d": (10, -1),
            "c": (10, -2),
            "m": (10, -3),
            "u": (10, -6),
            "n": (10, -9),
            "p": (10, -12),
            "f": (10, -15),
            "a": (10, -18),
            "z": (10, -21),
            "y": (10, -24),
            "Yi": (2, 80),
            "Zi": (2, 70),
            "Ei": (2, 60),
            "Pi": (2, 50),
            "Ti": (2, 40),
            "Gi": (2, 30),
            "Mi": (2, 20),
            "ki": (2, 10),
        }
    )


def teardown_module(_module):
    from noc.core.cdag.node.probe import ProbeNode

    ProbeNode.reset_convert()
    ProbeNode.reset_scale()
