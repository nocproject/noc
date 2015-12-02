# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Synchronous RPC Client
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import itertools
from collections import defaultdict
import json
import logging
import time
import random
import socket
import errno
## Third-party modules
import tornado.httpclient
## NOC modules
from noc.core.service.catalog import ServiceCatalog


# Connection time
CONNECT_TIMEOUT = 1
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
RETRY_SOCKET_ERRORS = (errno.ECONNREFUSED, errno.EHOSTDOWN)


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
            headers = {}
            if calling_service:
                headers[CALLING_SERVICE_HEADER] = calling_service
            body = json.dumps(req)
            # Build service candidates
            services = catalog.get_service(service).listen
            if len(services) < RETRIES:
                services *= RETRIES
            # Call
            client = tornado.httpclient.HTTPClient()
            response = None
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
                try:
                    response = client.fetch(
                        "http://%s/api/sae/" % l,
                        method="POST",
                        body=body,
                        headers=headers,
                        connect_timeout=CONNECT_TIMEOUT,
                        request_timeout=REQUEST_TIMEOUT
                    )
                    break
                except tornado.httpclient.HTTPError, why:
                    if why.code == 599:
                        logger.debug("Timed out")
                        continue
                    raise RPCHTTPError("HTTP Error %s: %s" % (
                        why.code, why.message))
                except socket.error as e:
                    if e.args[0] in RETRY_SOCKET_ERRORS:
                        logger.debug("Socket error: %s" % e)
                        continue
                    raise RPCException(str(e))
                except Exception, why:
                    raise RPCException(why)
            if not response:
                raise RPCNoService(
                    "No active service %s found" % service
                )
            data = json.loads(response.body)
            if data.get("error"):
                raise RPCRemoteError(data["error"])
            t = time.time() - t0
            logger.debug("[<CALL] %s (%.2fms)", self.method, t * 1000)
            return data["result"]

    def __init__(self, service, calling_service=None):
        self._service = service
        self._calling_service = calling_service

    def __getattr__(self, item):
        if item.startswith("_"):
            return self.__dict__[item]
        else:
            return self.CallProxy(self, item)


catalog = ServiceCatalog()
