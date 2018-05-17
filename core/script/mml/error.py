# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# MML errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.error import (ERR_MML_UNKNOWN, ERR_MML_CONNECTION_REFUSED,
                            ERR_MML_AUTH_FAILED, ERR_MML_BAD_RESPONSE)
from ..cli.error import CLIError


class MMLError(CLIError):
    default_code = ERR_MML_UNKNOWN
    default_msg = "MML Error"


class MMLConnectionRefused(MMLError):
    default_code = ERR_MML_CONNECTION_REFUSED
    default_msg = "Connection refused"


class MMLAuthFailed(MMLError):
    default_code = ERR_MML_AUTH_FAILED
    default_msg = "Authentication failed"


class MMLBadResponse(MMLError):
    default_code = ERR_MML_BAD_RESPONSE
    default_msg = "Bad MML Response"
