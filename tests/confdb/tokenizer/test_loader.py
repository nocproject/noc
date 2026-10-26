# ----------------------------------------------------------------------
# Test tokenizer loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.tokenizer.base import BaseTokenizer, tokenizer_loader


@pytest.mark.parametrize("name", ["ini", "line", "context", "indent", "curly", "routeros"])
def test_loader(name: str) -> None:
    t = tokenizer_loader.get(name)
    assert t is not None
    assert t.name == name
    assert issubclass(t, BaseTokenizer)
