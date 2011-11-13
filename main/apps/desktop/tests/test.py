# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.desktop unittests
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import AjaxTestCase
from noc.lib.version import get_version


class DesktopTestCase(AjaxTestCase):
    app = "main.desktop"
    users = {
        "superuser": {
            "is_superuser": True
        },
        "user": {
            "is_superuser": False
        }
    }

    def test_desktop(self):
        # Anonymous
        status, r1 = self.get("/")
        self.assertEqual(status, self.HTTP_OK)
        # Authenticated
        status, r2 = self.get("/", user="user")
        self.assertEqual(status, self.HTTP_OK)
        # Superuser
        status, r3 = self.get("/", user="superuser")
        self.assertEqual(status, self.HTTP_OK)
        # Check all resulsts match
        self.assertEqual(r1, r2)
        self.assertEqual(r1, r3)
        # @todo: check result for CSS and JS
        self.assertIn("</html>", r1)

    def test_api_version(self):
        version = get_version()
        # Anonymous
        status, r = self.get("/version/")
        self.assertEqual(status, self.HTTP_OK)
        self.assertEqual(r, version)
        # Authenticated
        status, r = self.get("/version/", user="user")
        self.assertEqual(status, self.HTTP_OK)
        self.assertEqual(r, version)
        # Superuser
        status, r = self.get("/version/", user="superuser")
        self.assertEqual(status, self.HTTP_OK)
        self.assertEqual(r, version)

    def test_api_is_logged(self):
        # Anonymous
        status, r = self.get("/is_logged/")
        self.assertEqual(status, self.HTTP_OK)
        self.assertEqual(r, False)
        # Authenticated
        status, r = self.get("/is_logged/", user="user")
        self.assertEqual(status, self.HTTP_OK)
        self.assertEqual(r, True)
        # Superuser
        status, r = self.get("/is_logged/", user="superuser")
        self.assertEqual(status, self.HTTP_OK)
        self.assertEqual(r, True)

    def test_login(self):
        status, r = self.post("/login/", data={"username": "user",
                                               "password": "user"})
        self.assertEqual(status, self.HTTP_OK)
        # self.assertEqual(r, True)  # Will not work due to auth. hook

    def test_navigation(self):
        # Anonymous
        status, r = self.get("/navigation/")
        self.assertEqual(status, self.HTTP_OK)
        # Authenticated
        status, r = self.get("/navigation/", user="user")
        self.assertEqual(status, self.HTTP_OK)
        # Superuser
        status, r = self.get("/navigation/", user="superuser")
        self.assertEqual(status, self.HTTP_OK)
