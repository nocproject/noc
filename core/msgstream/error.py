# ----------------------------------------------------------------------
# MsgStream errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.error import (
    NOCError,
    ERR_MSGSTREAM_UNKNOWN,
    ERR_MSGSTREAM_NOT_FOUND,
    ERR_MSGSTREAM_ALREADY_EXISTS,
    ERR_MSGSTREAM_CHANNEL_CLOSED,
    ERR_MSGSTREAM_UNAVAILABLE,
    ERR_RPC_MESSAGE_SIZE_EXCEEDED,
)


class MsgStreamError(NOCError):
    default_code = ERR_MSGSTREAM_UNKNOWN


class ErrorNotFound(MsgStreamError):
    default_code = ERR_MSGSTREAM_NOT_FOUND


class ErrorAlreadyExists(MsgStreamError):
    default_code = ERR_MSGSTREAM_ALREADY_EXISTS


class ErrorChannelClosed(MsgStreamError):
    default_code = ERR_MSGSTREAM_CHANNEL_CLOSED


class ErrorUnavailable(MsgStreamError):
    default_code = ERR_MSGSTREAM_UNAVAILABLE


class ErrorMessageSizeExceeded(MsgStreamError):
    default_code = ERR_RPC_MESSAGE_SIZE_EXCEEDED
