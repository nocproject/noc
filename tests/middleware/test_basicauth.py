# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test basic auth middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.http.base import HTTP
from noc.core.script.http.middleware.loader import loader


def test_basicauth():
    http = HTTP(None)
    mw_cls = loader.get_class("basicauth")
    middleware = mw_cls(http, user="user", password="password")
    url = "http://127.0.0.1"
    r_url, r_body, r_headers = middleware.process_post(url, {}, {})
    assert not r_body  # Should not be set
    assert r_headers == {"Authorization": b"Basic dXNlcjpwYXNzd29yZA=="}
    assert r_url == url  # Should not be changed
