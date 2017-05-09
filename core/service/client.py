# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Synchronous RPC Client
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import errno
## Third-party modules
import pycurl
## NOC modules
from .loader import get_service


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


def open_sync_rpc(name, pool=None, calling_service=None):
    get_service().open_rpc(name, pool=pool, sync=True)
