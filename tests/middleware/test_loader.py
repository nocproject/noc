# ----------------------------------------------------------------------
# Test middleware loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.script.http.middleware.base import BaseMiddleware, middleware_loader


@pytest.mark.parametrize(
    "name", ["urlsession", "urlrequestid", "jsonsession", "jsonrequestid", "basicauth"]
)
def test_loader(name: str) -> None:
    t = middleware_loader.get(name)
    assert t is not None
    assert t.name == name
    assert issubclass(t, BaseMiddleware)
