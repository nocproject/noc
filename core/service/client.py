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
import errno
import cStringIO
import random
## Third-party modules
import tornado.httpclient
import ujson
import pycurl
## NOC modules
from noc.core.service.catalog import ServiceCatalog


# Connection time
CONNECT_TIMEOUT = 20
# Total request time
REQUEST_TIMEOUT = 3600
#
RETRY_TIMEOUT = 1.0
RETRY_DELTA = 2.0
#
CALLING_SERVICE_HEADER = "X-NOC-Calling-Service"
#
RETRIES = 5
#
RETRY_SOCKET_ERRORS = (errno.ECONNREFUSED, errno.EHOSTDOWN,
                       errno.EHOSTUNREACH, errno.ENETUNREACH)

RETRY_CURL_ERRORS = set([
    pycurl.E_COULDNT_CONNECT,
    pycurl.E_OPERATION_TIMEDOUT,
    pycurl.E_RECV_ERROR
])


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
                    response_headers[name.strip().lower()] = value.strip()

                logger.debug("[%s] Sending request", l)
                buff = cStringIO.StringIO()
                response_headers = {}
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
                c.setopt(c.TCP_KEEPALIVE, 1)
                c.setopt(c.TCP_KEEPIDLE, 60)
                c.setopt(c.TCP_KEEPINTVL, 60)
                try:
                    c.perform()
                except pycurl.error as e:
                    errno, errstr = e
                    if errno in RETRY_CURL_ERRORS:
                        logger.debug("[%s] Got error %d (%s). Retry", l, errno, errstr)
                        return (None, None, None)
                    logger.debug("[%s] Got error %d (%s). Giving up", l, errno, errstr)
                    raise RPCException(str(e))
                finally:
                    code = c.getinfo(c.RESPONSE_CODE)
                    c.close()
                return (
                    code,
                    response_headers,
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
            if self.client._hints:
                services = self.client._hints
            else:
                services = catalog.get_service(service).listen
            if len(services) < RETRIES:
                services *= RETRIES
            # Call
            last = None
            st = RETRY_TIMEOUT
            orig_body = None
            for l in random.sample(services, RETRIES):
                # Sleep when trying same instance
                if l == last:
                    time.sleep(st + float(st) * (random.random() - 0.5) / 5)
                    st += RETRY_DELTA
                #
                last = l
                url = "http://%s/api/%s/" % (l, self.client._api)
                for nt in range(3):  # Limit redirects
                    code, response_headers, data = make_call(url, l, body)
                    if code == 200:
                        break
                    elif code is None:
                        break
                    elif code == 307:
                        url = response_headers.get("location")
                        ol = l
                        l = url.split("://", 1)[1].split("/")[0]
                        orig_body = body
                        body = data
                        logger.debug("[%s] Redirecting to %s", ol, url)
                    else:
                        raise RPCException("Invalid return code: %s %s" % (code, url))
                if code is None:
                    if orig_body:
                        body = orig_body
                        orig_body = None
                    continue
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

    def __init__(self, service, calling_service=None, hints=None):
        self._service = service
        self._api = service.split("-")[0]
        self._calling_service = calling_service
        self._hints = hints

    def __getattr__(self, item):
        if item.startswith("_"):
            return self.__dict__[item]
        else:
            return self.CallProxy(self, item)


catalog = ServiceCatalog()
