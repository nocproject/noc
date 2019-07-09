# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test tokenizer loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.tokenizer.loader import loader
from noc.core.confdb.tokenizer.base import BaseTokenizer


@pytest.mark.parametrize("name", ["ini", "line", "context", "indent", "curly", "routeros"])
def test_loader(name):
    t = loader.get_class(name)
    assert t is not None
    assert t.name == name
    assert issubclass(t, BaseTokenizer)
