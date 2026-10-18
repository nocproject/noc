# ----------------------------------------------------------------------
# Test middleware loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.script.http.middleware.base import middleware_loader
from noc.core.script.http.middleware.base import BaseMiddleware


@pytest.mark.parametrize(
    "name", ["urlsession", "urlrequestid", "jsonsession", "jsonrequestid", "basicauth"]
)
def test_loader(name):
    t = middleware_loader.get(name)
    assert t is not None
    assert t.name == name
    assert issubclass(t, BaseMiddleware)
