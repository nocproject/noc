# ----------------------------------------------------------------------
# Test node loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.cdag.node.base import node_loader


@pytest.mark.parametrize("name", list(node_loader.keys()))
def test_node_loader(name: str) -> None:
    node_cls = node_loader.get(name)
    assert node_cls
    assert node_cls.name == name
