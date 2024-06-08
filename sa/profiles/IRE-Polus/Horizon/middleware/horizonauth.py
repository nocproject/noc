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
from noc.core.http.sync_client import HttpClient


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
        with HttpClient(
            headers={"Content-Type": b"application/json"},
            timeout=60,
            allow_proxy=False,
            validate_cert=False,
        ) as client:
            code, resp_headers, result = client.post(self.http.get_url("/auth"), b)
            self.http._process_cookies(resp_headers)
            headers["Cookie"] = self.http.cookies.output(header="", attrs="value").lstrip().encode()
            self.http.logger.debug(
                "[%s] Response code %s, headers %s on: %s, body: %s",
                self.name,
                code,
                resp_headers,
                url,
                body,
            )
            return url, body, headers

