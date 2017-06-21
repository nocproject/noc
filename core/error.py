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
ERR_UNKNOWN = 0

#
# RPC Errors - 9000-9999
#
ERR_RPC_MIN_ERROR = 9000
ERR_RPC_MAX_ERROR = 9999

#
# SA Errors - 10000-10999
#

#
ERR_SA_MIN_ERROR = 10000
ERR_SA_MAX_ERROR = 10999

ERR_CLI_UNKNOWN = 10000
ERR_CLI_AUTH_FAILED = 10001
ERR_CLI_NO_SUPER_COMMAND = 10002
ERR_CLI_LOW_PRIVILEGES = 10003
ERR_CLI_SSH_PROTOCOL_ERROR = 10004


class NOCError(Exception):
    default_msg = None
    default_code = ERR_UNKNOWN

    def __init__(self, msg=None, code=None):
        super(NOCError, self).__init__(msg or self.default_msg)
        self.code = code or self.default_code
        metrics["err_%s" % self.code] += 1
