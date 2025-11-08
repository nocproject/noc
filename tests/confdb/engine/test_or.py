# ----------------------------------------------------------------------
# Test engine's `or` operator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.engine.base import Engine


@pytest.mark.parametrize(
    ("input", "query", "output"),
    [
        ({}, "False() or True()", [{}]),
        ({}, "(False() and False()) or True()", [{}]),
        ({}, "(True() and True()) or True()", [{}]),
        ({}, "(False() and False()) or False()", []),
        ({}, "(True() and True()) or False()", [{}]),
        ({}, "(True() and True() and True()) or False()", [{}]),
        ({}, "(True() and True() and True()) or True()", [{}]),
    ],
)
def test_org(input, query, output):
    e = Engine()
    assert list(e.query(query, **input)) == output
