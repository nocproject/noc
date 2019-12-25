# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test main.desktop application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from noc.core.version import version
from noc.config import config
from noc.core.comp import smart_text
from ..base import WebAPITest, gen_test


class TestDesktopAPI(WebAPITest):
    users = [
        {
            "username": "superuser",
            "email": "superuser@example.com",
            "first_name": "Mighty",
            "last_name": "Root",
        },
        {
            "username": "granted",
            "email": "granted@example.com",
            "first_name": "Granted",
            "last_name": "User",
        },
        {
            "username": "deprived",
            "email": "deprived@example.com",
            "first_name": "Deprived",
            "last_name": "Buddy",
        },
    ]

    @gen_test
    def test_is_logged(self):
        code, headers, body = yield self.fetch("/main/desktop/is_logged/")
        assert code == 200
        assert body is True

    @gen_test
    def test_html(self):
        code, headers, body = yield self.fetch("/main/desktop/")
        assert code == 200
        assert "</html>" in smart_text(body)

    @gen_test
    def test_about(self):
        code, headers, body = yield self.fetch("/main/desktop/about/")
        assert code == 200
        assert body.get("installation") == config.installation_name

    @gen_test
    def test_version(self):
        code, headers, body = yield self.fetch("/main/desktop/version/")
        assert code == 200
        assert body == version.version

    @gen_test
    def test_user_settings(self):
        for user in self.users:
            code, headers, body = yield self.fetch(
                "/main/desktop/user_settings/", user=user["username"]
            )
            assert code == 200
            assert body.get("username") == user["username"]
            assert body.get("email") == user["email"]
            assert body.get("first_name") == user["first_name"]
            assert body.get("last_name") == user["last_name"]
