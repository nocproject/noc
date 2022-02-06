# ----------------------------------------------------------------------
# Liftbridge errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from grpc import StatusCode
from grpc.experimental.aio import AioRpcError

# NOC modules
from noc.core.error import (
    NOCError,
    ERR_LIFTBRIDGE_UNKNOWN,
    ERR_LIFTBRIDGE_NOT_FOUND,
    ERR_LIFTBRIDGE_ALREADY_EXISTS,
    ERR_LIFTBRIDGE_CHANNEL_CLOSED,
    ERR_LIFTBRIDGE_UNAVAILABLE,
    ERR_RPC_MESSAGE_SIZE_EXCEEDED,
)


class LiftbridgeError(NOCError):
    default_code = ERR_LIFTBRIDGE_UNKNOWN


class ErrorNotFound(LiftbridgeError):
    default_code = ERR_LIFTBRIDGE_NOT_FOUND


class ErrorAlreadyExists(LiftbridgeError):
    default_code = ERR_LIFTBRIDGE_ALREADY_EXISTS


class ErrorChannelClosed(LiftbridgeError):
    default_code = ERR_LIFTBRIDGE_CHANNEL_CLOSED


class ErrorUnavailable(LiftbridgeError):
    default_code = ERR_LIFTBRIDGE_UNAVAILABLE


class ErrorMessageSizeExceeded(LiftbridgeError):
    default_code = ERR_RPC_MESSAGE_SIZE_EXCEEDED


RPC_CODE_TO_ERR = {
    StatusCode.ALREADY_EXISTS: ErrorAlreadyExists,
    StatusCode.NOT_FOUND: ErrorNotFound,
    StatusCode.UNAVAILABLE: ErrorUnavailable,
    StatusCode.RESOURCE_EXHAUSTED: ErrorMessageSizeExceeded,
}


class rpc_error(object):
    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, AioRpcError):
            code = exc_val.code()
            details = exc_val.details()
            xcls = RPC_CODE_TO_ERR.get(code) or LiftbridgeError
            raise xcls(details)
