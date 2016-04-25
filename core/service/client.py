# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Synchronous RPC Client
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import itertools
from collections import defaultdict
import logging
import time
import random
import socket
import errno
import cStringIO
## Third-party modules
import tornado.httpclient
import ujson
import pycurl
## NOC modules
from noc.core.service.catalog import ServiceCatalog


# Connection time
CONNECT_TIMEOUT = 3
# Total request time
REQUEST_TIMEOUT = 3600
#
RETRY_TIMEOUT = 1.0
RETRY_DELTA = 0.5
#
CALLING_SERVICE_HEADER = "X-NOC-Calling-Service"
#
RETRIES = 5
#
RETRY_SOCKET_ERRORS = (errno.ECONNREFUSED, errno.EHOSTDOWN,
                       errno.EHOSTUNREACH, errno.ENETUNREACH)


class RPCError(Exception):
    pass


class RPCHTTPError(RPCError):
    pass


class RPCException(RPCError):
    pass


class RPCNoService(RPCError):
    pass


class RPCRemoteError(RPCError):
    pass


class RPCClient(object):
    _tids = defaultdict(itertools.count)

    class CallProxy(object):
        def __init__(self, client, method):
            self.client = client
            self.method = method

        def __call__(self, *args):
            def make_call(url, l, body):
                """
                Perform POST
                :returns: code, headers, data
                """
                def process_headers(l):
                    if ":" not in l:
                        return
                    name, value = l.split(":", 1)
                    headers[name.strip().lower()] = value.strip()

                logger.debug("Sending request to %s", l)
                buff = cStringIO.StringIO()
                headers = {}
                c = pycurl.Curl()
                c.setopt(c.URL, url)
                c.setopt(c.POST, 1)
                c.setopt(c.POSTFIELDS, body)
                if headers:
                    c.setopt(c.HTTPHEADER, headers)
                c.setopt(c.WRITEDATA, buff)
                c.setopt(c.NOPROXY, "*")
                c.setopt(c.RESOLVE, ["%s:%s" % (l, l.split(":")[0])])
                c.setopt(c.TIMEOUT, REQUEST_TIMEOUT)
                c.setopt(c.CONNECTTIMEOUT, CONNECT_TIMEOUT)
                c.setopt(c.HEADERFUNCTION, process_headers)
                try:
                    c.perform()
                except pycurl.error as e:
                    # @todo: Retry on timeout
                    raise RPCException(str(e))
                finally:
                    code = c.getinfo(c.RESPONSE_CODE)
                    c.close()
                return (
                    code,
                    headers,
                    buff.getvalue()
                )

            t0 = time.time()
            service = self.client._service
            calling_service = self.client._calling_service
            logger = logging.getLogger("rpc.%s" % service)
            logger.debug("[>CALL] %s()", self.method)
            # Prepare request
            req = {
                "id": RPCClient._tids[service].next(),
                "method": self.method,
                "params": list(args)
            }
            headers = []
            if calling_service:
                headers += ["%s: %s" % (CALLING_SERVICE_HEADER,
                                        calling_service)]
            body = ujson.dumps(req)
            # Build service candidates
            services = catalog.get_service(service).listen
            if len(services) < RETRIES:
                services *= RETRIES
            # Call
            last = None
            st = RETRY_TIMEOUT
            for l in random.sample(services, RETRIES):
                # Sleep when trying same instance
                if l == last:
                    time.sleep(st)
                    st += RETRY_DELTA
                #
                last = l
                logger.debug("Sending request to %s", l)
                url = "http://%s/api/%s/" % (l, self.client._api)
                for nt in range(3):  # Limit redirects
                    code, headers, data = make_call(url, l, body)
                    if code == 200:
                        break
                    elif code == 307:
                        url = headers.get("location")
                        l = url.split("://", 1)[1].split("/")[0]
                        body = data
                        logger.debug("Redirecting to %s", url)
                    else:
                        raise RPCException("Invalid return code: %s" % code)
                if code != 200:
                    raise RPCException("Redirects limit exceeded")
                try:
                    data = ujson.loads(data)
                except ValueError as e:
                    raise RPCRemoteError("Failed to decode JSON: %s" % e)
                if data.get("error"):
                    raise RPCRemoteError(data["error"])
                t = time.time() - t0
                logger.debug("[<CALL] %s (%.2fms)", self.method, t * 1000)
                return data["result"]
            raise RPCNoService(
                "No active service %s found" % service
            )

    def __init__(self, service, calling_service=None):
        self._service = service
        self._api = service.split("-")[0]
        self._calling_service = calling_service

    def __getattr__(self, item):
        if item.startswith("_"):
            return self.__dict__[item]
        else:
            return self.CallProxy(self, item)


catalog = ServiceCatalog()
