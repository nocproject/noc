# ----------------------------------------------------------------------
# Test JSONSession
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
    ("body", "config", "session_id", "expected"),
    [
        ({}, {}, None, {}),
        ({}, {}, 123, {"session_id": "123"}),
        ({}, {}, "12345", {"session_id": "12345"}),
        ({}, {"session_param": "sid"}, 123, {"sid": "123"}),
        ({}, {"session_param": "sid"}, "12345", {"sid": "12345"}),
    ],
)
def test_jsonsession(body, config, session_id, expected):
    http = HTTP(None)
    http.set_session_id(session_id)
    mw_cls = loader.get_class("jsonsession")
    middleware = mw_cls(http, **config)
    url = "http://127.0.0.1"
    # POST
    r_url, r_body, r_headers = middleware.process_post(url, body.copy(), {})
    assert r_body == expected
    assert not r_headers  # Should not be set
    assert r_url == url  # Should not be changed
    # PUT
    r_url, r_body, r_headers = middleware.process_put(url, body.copy(), {})
    assert r_body == expected
    assert not r_headers  # Should not be set
    assert r_url == url  # Should not be changed
