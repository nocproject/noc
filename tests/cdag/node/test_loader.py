# ----------------------------------------------------------------------
# Test node loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.cdag.node.loader import loader


@pytest.mark.parametrize("name", loader.find_classes())
def test_node_loader(name):
    node_cls = loader.get_class(name)
    assert node_cls
    assert node_cls.name == name
