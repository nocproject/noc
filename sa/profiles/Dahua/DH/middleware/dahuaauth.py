# ----------------------------------------------------------------------
# HTTP Dahua Auth Middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import orjson
import hashlib
import codecs

# NOC modules
from noc.core.script.http.middleware.base import BaseMiddleware
from noc.core.http.sync_client import HttpClient
from noc.core.comp import smart_bytes


class DahuaAuthMiddeware(BaseMiddleware):
    """
    Append HTTP Digest authorisation headers
    """

    name = "dahuaauth"

    def __init__(self, http):
        super().__init__(http)
        self.user = self.http.script.credentials.get("user")
        self.password = self.http.script.credentials.get("password")

    def get_auth(self, params):
        """
        Web JS
        i.getAuth = function(a, b, c) {
            switch (c = c || j.encryption) {
            case "Basic":
                return Base64.encode(a + ":" + b);
            case "Default":
                return hex_md5(a + ":" + j.random + ":" + hex_md5(a + ":" + j.realm + ":" + b));
            default:
                return b
            }
        :param params: response params dictionary
        :type params: dict
        :return: Password string
        :rtype: str
        """
        if params["encryption"] == "Basic":
            return codecs.encode("%s:%s" % (self.user, self.password), "base64")
        elif params["encryption"] == "Default":
            A1 = (
                hashlib.md5(smart_bytes("%s:%s:%s" % (self.user, params["realm"], self.password)))
                .hexdigest()
                .upper()
            )
            return (
                hashlib.md5(smart_bytes("%s:%s:%s" % (self.user, params["random"], A1)))
                .hexdigest()
                .upper()
            )
        return self.password

    def process_post(self, url, body, headers):
        """
        Dahua Web auth procedure
        :param url:
        :param body:
        :param headers:
        :return:
        """
        if self.http.session_id:
            body["session"] = self.http.session_id
            return url, body, headers
        if not headers:
            headers = {}
        # First query - /RPC2_Login
        auth_url = self.http.get_url("/RPC2_Login")

        with HttpClient(
            url,
            headers=headers,
            timeout=60,
            allow_proxy=False,
            validate_cert=False,
        ) as client:
            code, resp_headers, result = client.post(
                auth_url,
                orjson.dumps(
                    {
                        "method": "global.login",
                        "params": {
                            "userName": self.user,
                            "password": "",
                            "clientType": "Web3.0",
                            "loginType": "Direct",
                        },
                        "id": self.http.request_id,
                    },
                ),
            )
            r = orjson.loads(result)
            session = r["session"]
            self.http.set_session_id(session)
            password = self.get_auth(r["params"])

            client.post(
                auth_url,
                orjson.dumps(
                    {
                        "method": "global.login",
                        "params": {
                            "userName": self.user,
                            "password": password,
                            "clientType": "Web3.0",
                            "loginType": "Direct",
                        },
                        "id": self.http.request_id,
                        "session": session,
                    }
                ),
            )
            self.http.request_id += 2
            body["session"] = self.http.session_id
            return url, body, headers
