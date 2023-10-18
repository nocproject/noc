# ----------------------------------------------------------------------
# HTTP Horizon Auth Middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import orjson

# NOC modules
from noc.core.script.http.middleware.base import BaseMiddleware
from noc.core.http.client import fetch_sync


class HorizonAuthMiddeware(BaseMiddleware):
    """
    Authenticate
    """

    name = "horizonauth"

    def process_request(self, url, body, headers):
        if not headers:
            headers = {}
        if self.http.cookies:
            return url, body, headers
        # Auth
        # self.logger.debug("[%s] Process middleware on: %s", self.name, url)
        # First query - 401
        b = orjson.dumps(
            {
                "login": self.http.script.credentials.get("user"),
                "password": self.http.script.credentials.get("password"),
            }
        )
        code, resp_headers, result = fetch_sync(
            url=self.http.get_url("/auth"),
            body=b,
            method="POST",
            headers={"Content-Type": "application/json"},
            request_timeout=60,
            follow_redirects=True,
            allow_proxy=False,
            validate_cert=False,
        )
        self.http._process_cookies(resp_headers)
        headers["Cookie"] = self.http.cookies.output(header="", attrs="value").lstrip()
        self.http.logger.debug(
            "[%s] Response code %s, headers %s on: %s, body: %s",
            self.name,
            code,
            resp_headers,
            url,
            body,
        )
        return url, body, headers
