# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Synchronous RPC Client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import errno
# NOC modules
from .loader import get_service
from .error import (RPCError, RPCHTTPError, RPCException, RPCNoService,
                    RPCRemoteError)
from noc.config import config

# Connection time
CONNECT_TIMEOUT = config.rpc.sync_connect_timeout
# Total request time
REQUEST_TIMEOUT = config.rpc.sync_request_timeout
#
RETRY_TIMEOUT = config.rpc.sync_retry_timeout
RETRY_DELTA = config.rpc.sync_retry_delta
#
CALLING_SERVICE_HEADER = "X-NOC-Calling-Service"
#
RETRIES = config.rpc.sync_retries
#
RETRY_SOCKET_ERRORS = (errno.ECONNREFUSED, errno.EHOSTDOWN,
                       errno.EHOSTUNREACH, errno.ENETUNREACH)


def open_sync_rpc(name, pool=None, calling_service=None, hints=None):
    return get_service().open_rpc(name, pool=pool,
                                  sync=True, hints=hints)
