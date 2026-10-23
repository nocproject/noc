# ----------------------------------------------------------------------
# RTSP errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.error import (
    ERR_RTSP_UNKNOWN,
    ERR_RTSP_CONNECTION_REFUSED,
    ERR_RTSP_AUTH_FAILED,
    ERR_RTSP_BAD_RESPONSE,
)
from ..cli.error import CLIError


class RTSPError(CLIError):
    default_code = ERR_RTSP_UNKNOWN
    default_msg = "RTSP Error"


class RTSPConnectionRefused(RTSPError):
    default_code = ERR_RTSP_CONNECTION_REFUSED
    default_msg = "Connection refused"


class RTSPAuthFailed(RTSPError):
    default_code = ERR_RTSP_AUTH_FAILED
    default_msg = "Authentication failed"


class RTSPBadResponse(RTSPError):
    default_code = ERR_RTSP_BAD_RESPONSE
    default_msg = "Bad MML Response"
