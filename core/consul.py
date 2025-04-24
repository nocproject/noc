# ----------------------------------------------------------------------
# Consul client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
import consul.base

# NOC modules
from noc.config import config
from noc.core.http.async_client import HttpClient
from noc.core.comp import DEFAULT_ENCODING

ConsulRepeatableCodes = {500, 503, 598, 599}
ConsulRepeatableErrors = consul.base.Timeout


class ConsulHTTPClient(consul.base.HTTPClient):
    """
    asyncio version of consul http client
    """

    async def _request(self, callback, url, method="GET", body: Optional[str] = None):
        async with HttpClient(
            connect_timeout=config.consul.connect_timeout,
            timeout=config.consul.request_timeout,
            validate_cert=self.verify,
        ) as client:
            code, headers, body = await client.request(
                method,
                url,
                body=body.encode(DEFAULT_ENCODING) if body is not None else body,
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
