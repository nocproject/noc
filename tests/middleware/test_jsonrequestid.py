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
    ("body", "config", "request_id", "expected"),
    [
        ({}, {}, 123, {"request_id": 123}),
        ({"x": 1}, {}, 123, {"request_id": 123, "x": 1}),
        ({}, {"request_id_param": "rid"}, 456, {"rid": 456}),
        ({"a": "b"}, {"request_id_param": "rid"}, 456, {"rid": 456, "a": "b"}),
    ],
)
def test_jsonsession(body, config, request_id, expected):
    http = HTTP(None)
    http.request_id = request_id
    mw_cls = loader.get_class("jsonrequestid")
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
