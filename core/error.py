# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Base Error class and error codes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.perf import metrics

# Unknown error
NO_ERROR = 0
ERR_UNKNOWN = 1

#
# RPC Errors - 9000-9999
#
ERR_RPC_MIN_ERROR = 9000
ERR_RPC_MAX_ERROR = 9999

ERR_RPC_UNKNOWN = 9000
ERR_RPC_HTTP_ERROR = 9001
ERR_RPC_EXCEPTION = 9002
ERR_RPC_NO_SERVICE = 9003
ERR_RPC_REMOTE_ERROR = 9004

#
# SA Errors - 10000-10999
#

#
ERR_SA_MIN_ERROR = 10000
ERR_SA_MAX_ERROR = 10999
# CLI errors
ERR_CLI_UNKNOWN = 10000
ERR_CLI_AUTH_FAILED = 10001
ERR_CLI_NO_SUPER_COMMAND = 10002
ERR_CLI_LOW_PRIVILEGES = 10003
ERR_CLI_SSH_PROTOCOL_ERROR = 10004
ERR_CLI_CONNECTION_REFUSED = 10005
# Script errors
ERR_SCRIPT_UNKNOWN = 10100
ERR_SCRIPT_SYNTAX = 10101
ERR_SCRIPT_OPERATION = 10102
ERR_SCRIPT_NOT_SUPPORTED = 10103
ERR_SCRIPT_UNEXPECTED_RESULT = 10104
# SNMP errors
ERR_SNMP_UNKNOWN = 10200
ERR_SNMP_TIMEOUT = 10201
ERR_SNMP_FATAL_TIMEOUT = 10202
# HTTP error
ERR_HTTP_UNKNOWN = 10300


class NOCError(Exception):
    default_msg = None
    default_code = ERR_UNKNOWN

    def __init__(self, msg=None, code=None):
        super(NOCError, self).__init__(msg or self.default_msg)
        self.code = code or self.default_code
        metrics["err_%s" % self.code] += 1
