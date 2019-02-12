# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test engine's Set() predicate
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
# NOC modules
from noc.core.confdb.engine.base import Engine


@pytest.mark.parametrize("input,query,output", [
    # Noop
    ({}, "Set()", [{}]),
    # Set one value to empty context
    ({}, "Set(x=1)", [{"x": 1}]),
    # Set two values to empty context
    ({}, "Set(x=1, y=2)", [{"x": 1, "y": 2}]),
    # Set one value to filled context
    ({"x": 1}, "Set(y=2)", [{"x": 1, "y": 2}]),
    # Overwrite value of context
    ({"x": 1, "y": 2}, "Set(x=3)", [{"x": 3, "y": 2}]),
    # Iterate single list over empty context
    ({}, "Set(x=[1, 2, 3])", [{"x": 1}, {"x": 2}, {"x": 3}]),
    # Product two lists over empty context
    ({}, "Set(x=[1, 2], y=[3, 4])",
     [{"x": 1, "y": 3}, {"x": 2, "y": 3}, {"x": 1, "y": 4}, {"x": 2, "y": 4}]),
    # Product two lists over filled context
    ({"z": 3}, "Set(x=[1, 2], y=[3, 4])", [
        {"x": 1, "y": 3, "z": 3},
        {"x": 2, "y": 3, "z": 3},
        {"x": 1, "y": 4, "z": 3},
        {"x": 2, "y": 4, "z": 3}
    ]),
    # Product two list over production context
    ({"z": [3, 7]}, "Set(x=[1, 2], y=[3, 4])", [
        {"x": 1, "y": 3, "z": 3},
        {"x": 2, "y": 3, "z": 3},
        {"x": 1, "y": 4, "z": 3},
        {"x": 2, "y": 4, "z": 3},
        {"x": 1, "y": 3, "z": 7},
        {"x": 2, "y": 3, "z": 7},
        {"x": 1, "y": 4, "z": 7},
        {"x": 2, "y": 4, "z": 7}
    ]),
    # Set after set
    ({"z": 3}, "Set(x=1) and Set(y=2)", [{"x": 1, "y": 2, "z": 3}]),
    ({"z": 3}, "Set(x=1, y=2) and Set(k=3)", [{"k": 3, "x": 1, "y": 2, "z": 3}])
])
def test_set(input, query, output):
    e = Engine()
    assert list(e.query(query, **input)) == output
