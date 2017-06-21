# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Service Errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.error import (
    NOCError, ERR_RPC_UNKNOWN, ERR_RPC_HTTP_ERROR, ERR_RPC_NO_SERVICE,
    ERR_RPC_EXCEPTION, ERR_RPC_REMOTE_ERROR)


class RPCError(NOCError):
    default_code = ERR_RPC_UNKNOWN


class RPCHTTPError(RPCError):
    default_code = ERR_RPC_HTTP_ERROR


class RPCException(RPCError):
    default_code = ERR_RPC_EXCEPTION


class RPCNoService(RPCError):
    default_code = ERR_RPC_NO_SERVICE


class RPCRemoteError(RPCError):
    default_code = ERR_RPC_REMOTE_ERROR

    def __init__(self, msg, remote_code=None):
        super(RPCRemoteError, self).__init__(msg)
        self.remote_code = remote_code
