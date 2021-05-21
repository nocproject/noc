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
