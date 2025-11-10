# ----------------------------------------------------------------------
# Test engine's Not() predicate
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.engine.base import Engine


@pytest.mark.parametrize(
    ("input", "query", "output"),
    [
        # Empty context
        ({}, "not True()", []),
        ({}, "not False()", [{}]),
        ({}, "not (True() and False())", [{}]),
    ],
)
def test_not(input, query, output):
    e = Engine()
    assert list(e.query(query, **input)) == output
