# ----------------------------------------------------------------------
# Consul client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import consul.base

# NOC modules
from noc.config import config
from noc.core.http.client import fetch

ConsulRepeatableCodes = {500, 503, 598, 599}
ConsulRepeatableErrors = consul.base.Timeout


class ConsulHTTPClient(consul.base.HTTPClient):
    """
    asyncio version of consul http client
    """

    async def _request(self, callback, url, method="GET", body=None):
        code, headers, body = await fetch(
            url,
            method=method,
            body=body,
            connect_timeout=config.consul.connect_timeout,
            request_timeout=config.consul.request_timeout,
            validate_cert=self.verify,
        )
        if code in ConsulRepeatableCodes:
            raise consul.base.Timeout
        return callback(consul.base.Response(code=code, headers=headers, body=body))

    def get(self, callback, path, params=None):
        url = self.uri(path, params)
        return self._request(callback, url, method="GET")

    def put(self, callback, path, params=None, data=""):
        url = self.uri(path, params)
        return self._request(callback, url, method="PUT", body="" if data is None else data)

    def delete(self, callback, path, params=None):
        url = self.uri(path, params)
        return self._request(callback, url, method="DELETE")

    def post(self, callback, path, params=None, data=""):
        url = self.uri(path, params)
        return self._request(callback, url, method="POST", body=data)


class ConsulClient(consul.base.Consul):
    def connect(self, host, port, scheme, verify=True, cert=None):
        return ConsulHTTPClient(host, port, scheme, verify=verify)
