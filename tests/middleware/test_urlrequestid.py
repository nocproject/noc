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
        # Default request parameter
        ("http://127.0.0.1", {}, "http://127.0.0.1?request_id={0}"),
        ("http://127.0.0.1?q", {}, "http://127.0.0.1?q&request_id={0}"),
        ("http://127.0.0.1?x=y", {}, "http://127.0.0.1?x=y&request_id={0}"),
        # 'sid' request parameter
        ("http://127.0.0.1", {"request_id_param": "_dc"}, "http://127.0.0.1?_dc={0}"),
        ("http://127.0.0.1?q", {"request_id_param": "_dc"}, "http://127.0.0.1?q&_dc={0}"),
        ("http://127.0.0.1?x=y", {"request_id_param": "_dc"}, "http://127.0.0.1?x=y&_dc={0}"),
    ],
)
def test_(url, config, expected):
    http = HTTP(None)
    mw_cls = loader.get_class("urlrequestid")
    middleware = mw_cls(http, **config)
    for _ in range(3):
        r_url, r_body, r_headers = middleware.process_request(url, {}, {})
        assert not r_body  # Should not be set
        assert not r_headers  # Should not be set
        r_expected = expected.format(http.request_id)
        assert r_url == r_expected  # Should not be changed due to empty request
        http.request_id += 1
