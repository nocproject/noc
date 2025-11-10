# ----------------------------------------------------------------------
# Test URLSessionMiddleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.script.http.base import HTTP
from noc.core.script.http.middleware.loader import loader


@pytest.mark.parametrize(
    ("url", "config", "expected"),
    [
        # Default session parameter
        ("http://127.0.0.1", {}, "http://127.0.0.1?session_id={0}"),
        ("http://127.0.0.1?q", {}, "http://127.0.0.1?q&session_id={0}"),
        ("http://127.0.0.1?x=y", {}, "http://127.0.0.1?x=y&session_id={0}"),
        # 'sid' session parameter
        ("http://127.0.0.1", {"session_param": "sid"}, "http://127.0.0.1?sid={0}"),
        ("http://127.0.0.1?q", {"session_param": "sid"}, "http://127.0.0.1?q&sid={0}"),
        ("http://127.0.0.1?x=y", {"session_param": "sid"}, "http://127.0.0.1?x=y&sid={0}"),
    ],
)
def test_(url, config, expected):
    http = HTTP(None)
    mw_cls = loader.get_class("urlsession")
    middleware = mw_cls(http, **config)
    # No session yet
    r_url, r_body, r_headers = middleware.process_request(url, {}, {})
    assert not r_body  # Should not be set
    assert not r_headers  # Should not be set
    assert r_url == url  # Should not be changed due to empty session
    # Set session as number
    session_id = 123
    http.set_session_id(session_id)
    r_url, r_body, r_headers = middleware.process_request(url, {}, {})
    assert not r_body  # Should not be set
    assert not r_headers  # Should not be set
    r_expected = expected.format(session_id)
    assert r_url == r_expected  # Should not be changed due to empty session
    # Set session as string
    session_id = "12345"
    http.set_session_id(session_id)
    r_url, r_body, r_headers = middleware.process_request(url, {}, {})
    assert not r_body  # Should not be set
    assert not r_headers  # Should not be set
    r_expected = expected.format(session_id)
    assert r_url == r_expected  # Should not be changed due to empty session
