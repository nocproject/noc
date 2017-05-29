# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Consul client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import tornado.gen
import tornado.ioloop
import tornado.httpclient
import consul.base
import consul.tornado


CONSUL_CONNECT_TIMEOUT = 5
CONSUL_REQUEST_TIMEOUT = 3600
CONSUL_NEAR_RETRY_TIMEOUT = 1

ConsulRepeatableErrors = consul.base.Timeout


class ConsulHTTPClient(consul.tornado.HTTPClient):
    """
    Gentler version of tornado http client
    """
    @tornado.gen.coroutine
    def _request(self, callback, request):
        client = tornado.httpclient.AsyncHTTPClient(
            force_instance=True,
            max_clients=1
        )
        try:
            response = yield client.fetch(request)
        except tornado.httpclient.HTTPError as e:
            if e.code == 599:
                raise consul.base.Timeout
            response = e.response
        finally:
            client.close()
            # Resolve CurlHTTPClient circular dependencies
            client._force_timeout_callback = None
            client._multi = None
        raise tornado.gen.Return(callback(self.response(response)))

    def get(self, callback, path, params=None):
        uri = self.uri(path, params)
        request = tornado.httpclient.HTTPRequest(
            uri,
            method="GET",
            validate_cert=self.verify,
            connect_timeout=CONSUL_CONNECT_TIMEOUT,
            request_timeout=CONSUL_REQUEST_TIMEOUT
        )
        return self._request(callback, request)

    def put(self, callback, path, params=None, data=""):
        uri = self.uri(path, params)
        request = tornado.httpclient.HTTPRequest(
            uri,
            method="PUT",
            body="" if data is None else data,
            validate_cert=self.verify,
            connect_timeout=CONSUL_CONNECT_TIMEOUT,
            request_timeout=CONSUL_REQUEST_TIMEOUT
        )
        return self._request(callback, request)

    def delete(self, callback, path, params=None):
        uri = self.uri(path, params)
        request = tornado.httpclient.HTTPRequest(
            uri,
            method="DELETE",
            validate_cert=self.verify,
            connect_timeout=CONSUL_CONNECT_TIMEOUT,
            request_timeout=CONSUL_REQUEST_TIMEOUT
        )
        return self._request(callback, request)

    def post(self, callback, path, params=None, data=''):
        uri = self.uri(path, params)
        request = tornado.httpclient.HTTPRequest(
            uri,
            method="POST",
            body=data,
            validate_cert=self.verify,
            connect_timeout=CONSUL_CONNECT_TIMEOUT,
            request_timeout=CONSUL_REQUEST_TIMEOUT
        )
        return self._request(callback, request)


class ConsulClient(consul.base.Consul):
    def connect(self, host, port, scheme, verify=True):
        return ConsulHTTPClient(host, port, scheme, verify=verify)
