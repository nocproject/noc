# ----------------------------------------------------------------------
# ConfigFactory tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.cdag.graph import CDAG
from noc.core.cdag.factory.config import ConfigCDAGFactory, GraphConfig, NodeItem, InputItem

CONFIG = GraphConfig(
    nodes=[
        NodeItem(name="n01", type="value", description="Value of 1", config={"value": 1.0}),
        NodeItem(name="n02", type="value", description="Value of 2", config={"value": 2.0}),
        NodeItem(
            name="n03",
            type="add",
            description="Add values",
            inputs=[InputItem(name="x", node="n01"), InputItem(name="y", node="n02")],
        ),
        NodeItem(name="n04", type="state", inputs=[InputItem(name="x", node="n03")]),
    ]
)


@pytest.mark.parametrize(("config", "out_state"), [(CONFIG, {"n04": {"value": 3.0}})])
def test_config_factory(config, out_state):
    # Empty graph with no state
    cdag = CDAG("test", {})
    # Apply config
    factory = ConfigCDAGFactory(cdag, CONFIG)
    factory.construct()
    # Check nodes
    for item in CONFIG.nodes:
        node = cdag[item.name]
        assert node
        assert node.node_id == item.name
        if item.description:
            assert node.description == item.description
    # Compare final state with expected
    assert cdag.get_state() == out_state


MISSED_CONFIG = GraphConfig(
    nodes=[
        NodeItem(name="n01", type="value", description="Value of 1", config={"value": 1.0}),
        NodeItem(
            name="n02!",
            type="value",
            description="Value of 2. Intentionally malformed id",
            config={"value": 2.0},
        ),
        NodeItem(
            name="n03",
            type="add",
            description="Add values",
            inputs=[InputItem(name="x", node="n01"), InputItem(name="y", node="n02")],
        ),
        NodeItem(name="n04", type="state", inputs=[InputItem(name="x", node="n03")]),
    ]
)


def test_config_missed_node():
    cdag = CDAG("test", {})
    # Apply config
    factory = ConfigCDAGFactory(cdag, MISSED_CONFIG)
    factory.construct()
    nodes = set(cdag.nodes)
    assert nodes == {"n01", "n02!"}


MATCHERS_CONFIG = GraphConfig(
    nodes=[
        NodeItem(name="n01", type="value", description="Value of 1", config={"value": 1.0}),
        NodeItem(name="n02", type="value", description="Value of 2", config={"value": 2.0}),
        NodeItem(
            name="n03",
            type="add",
            description="Add values",
            inputs=[InputItem(name="x", node="n01"), InputItem(name="y", node="n02")],
            match={"allow_sum": True},
        ),
        NodeItem(
            name="n04",
            type="state",
            inputs=[InputItem(name="x", node="n03")],
            match={"allow_sum": True, "allow_state": True},
        ),
    ]
)


@pytest.mark.parametrize(
    ("ctx", "expected_nodes"),
    [
        ({}, {"n01", "n02"}),
        ({"allow_sum": False}, {"n01", "n02"}),
        ({"allow_sum": True}, {"n01", "n02", "n03"}),
        ({"allow_sum": True, "allow_state": False}, {"n01", "n02", "n03"}),
        ({"allow_sum": True, "allow_state": True}, {"n01", "n02", "n03", "n04"}),
    ],
)
def test_config_matchers(ctx, expected_nodes):
    cdag = CDAG("test", {})
    # Apply config
    factory = ConfigCDAGFactory(cdag, MATCHERS_CONFIG, ctx=ctx)
    factory.construct()
    nodes = set(cdag.nodes)
    assert nodes == expected_nodes
