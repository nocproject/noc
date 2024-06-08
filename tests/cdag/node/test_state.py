# ----------------------------------------------------------------------
# Test StateNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .util import NodeCDAG


@pytest.mark.parametrize("value", [1, 1.0, 5])
def test_state_node(value):
    state = {}
    cdag = NodeCDAG("state", state=state)
    cdag.activate("x", value)
    ns = cdag.get_node().get_state()
    assert ns.value == value
    state = cdag.get_changed_state()
    assert state and ("node", "state") in state and "value" in state[("node", "state")]
    assert state[("node", "state")]["value"] == value
