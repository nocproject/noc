# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.Host
# Dummb profile to allow managed object creating
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import json
# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.http.client import fetch_sync

class Profile(BaseProfile):
    name = "Generic.Object"



    class http(object):
        """Switch context manager to use with "with" statement"""

        rx_coockie = re.compile("session_id=(?P<id>\S+);", re.MULTILINE)

        FORT_ACTIONS = {
            "connect":
                "%s/api/integration/v1/connect?login=%s&password=%s&lang=%s&timezone=%s",
            "disconnect":
                "%s/api/integration/v1/disconnect"
        }

        def __init__(self, script):
            self.script = script
            self.host = script.credentials.get("address", "")
            self.login = script.credentials.get("user", "")
            self.password = script.credentials.get("password", "")

        def __enter__(self):
            """Enter switch context"""
            user = self.login
            login = user.split("#")[0]
            code, headers, body = fetch_sync(
                self.FORT_ACTIONS["connect"] % (self.host, login, self.password, "ru-ru", +3),
                follow_redirects=True,
                allow_proxy=False
            )
            if code != 200:
                raise IOError("Invalid HTTP response: %s" % code)
            if self.rx_coockie.search(dict(headers)["Set-Cookie"]):
                h = self.rx_coockie.findall(dict(headers)["Set-Cookie"])
                self.coockies = {"Cookie": "SGUID=session_id=%s;" % h[0]}

            return {"coockies":self.coockies, "id": user.split("#")[1]}

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave switch context"""
            if exc_type is None:
                dcode, dheaders, dbody = fetch_sync(
                    self.FORT_ACTIONS["disconnect"] % self.host,
                    headers=self.coockies,
                    follow_redirects=True,
                    allow_proxy=False
                )
                if dcode != 200:
                    raise IOError("Invalid HTTP response: %s" % dcode)