# ----------------------------------------------------------------------
# HTTP Ubiquiti Auth Middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import orjson

# NOC modules
from noc.core.script.http.middleware.base import BaseMiddleware
from noc.core.http.sync_client import HttpClient


class UbiquitiAuthMiddeware(BaseMiddleware):
    """
    Authenticate
    """

    name = "ubiquityauth"

    def process_request(self, url, body, headers):
        if not headers:
            headers = {}
        if self.http.cookies:
            headers["X-Csrf-Token"] = self.http.cookies.get("csrf_token").value.encode()
            return url, body, headers
        # Auth
        # self.logger.debug("[%s] Process middleware on: %s", self.name, url)
        # First query - 401
        b = orjson.dumps(
            {
                "username": self.http.script.credentials.get("user"),
                "remember": False,
                "strict": True,
                "password": self.http.script.credentials.get("password"),
            }
        )
        with HttpClient(
            headers={"Content-Type": b"application/json"},
            timeout=60,
            allow_proxy=False,
            validate_cert=False,
        ) as client:
            code, resp_headers, result = client.post(self.http.get_url("/api/login"), b)
            self.http._process_cookies(resp_headers, allow_multiple_header=True)
            headers["Cookie"] = (
                self.http.cookies.output(header="", sep=";", attrs=["value"]).lstrip().encode()
            )
            self.http.logger.info(
                "[%s] Response code %s, headers %s on: %s, body: %s",
                self.name,
                code,
                list(resp_headers.items()),
                url,
                body,
            )
            return url, body, headers
