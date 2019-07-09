# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test engine's query compilations
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.engine.base import Engine


@pytest.mark.parametrize(
    "query",
    [
        "True()",
        "True() and True()",
        "True() and True() and True()",
        "(True() and True())",
        "Set(x=1, y=2) and True()",
    ],
)
def test_valid(query):
    e = Engine()
    e.compile(query)


@pytest.mark.parametrize("query", ["True("])
def test_invalid(query):
    e = Engine()
    with pytest.raises(SyntaxError):
        e.compile(query)


@pytest.mark.parametrize("query", ["True()", "True() and True()"])
def test_prepared_query(query):
    e = Engine()
    q = e.compile(query)
    e.query(q)
