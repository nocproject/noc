# ----------------------------------------------------------------------
# BaseNode tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.cdag.graph import CDAG


def test_missed_activate():
    cdag = CDAG("test", {})
    node = cdag.add_node("n01", "none")
    tx = cdag.begin()
    with pytest.raises(KeyError):
        tx.activate(node.name, "xxx", 1)


def test_add_input_fail():
    cdag = CDAG("test", {})
    node = cdag.add_node("n01", "none")
    # None node has "x" input by default
    inputs = list(node.iter_inputs())
    assert inputs == ["x"]
    # Add "y" dynamic input
    with pytest.raises(TypeError):
        node.add_input("y")
    inputs = list(node.iter_inputs())
    assert inputs == ["x"]
