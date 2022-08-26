# ----------------------------------------------------------------------
# Test node categories
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.cdag.node.loader import loader
from noc.core.cdag.node.base import Category

CATEGORIES = {
    Category.MATH: {
        "abs",
        "acos",
        "asin",
        "atan",
        "cos",
        "exp",
        "logistic",
        "neg",
        "relu",
        "softplus",
        "sin",
        "sqrt",
        "tan",
    },
    Category.OPERATION: {"add", "div", "mul", "sub"},
    Category.LOGICAL: {},
    Category.ACTIVATION: {"indicator", "logistic", "relu", "softplus"},
    Category.COMPARE: {"eq", "ne"},
    Category.DEBUG: {"state", "dump"},
    Category.UTIL: {"alarm", "key", "metrics", "none", "one", "probe", "composeprobe", "subgraph", "value"},
    Category.STATISTICS: {"mean", "std"},
    Category.ML: {"gauss"},
    Category.WINDOW: {"expdecay", "nth", "percentile", "sumstep"},
}


@pytest.mark.parametrize("name", loader.find_classes())
def test_node_loader(name):
    node_cls = loader.get_class(name)
    assert node_cls
    assert node_cls.categories, "Categories may not be empty"
    assert isinstance(node_cls.categories, list)
    # Check all categories are valid
    expected = {c for c in CATEGORIES if node_cls.name in CATEGORIES[c]}
    assert set(node_cls.categories) == expected
