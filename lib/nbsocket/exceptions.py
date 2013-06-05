# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## nbsocket exceptions
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import socket
import errno
import sys


class SocketError(Exception):
    message = "Socket Library Error"


class SocketNotImplemented(Exception):
    message = "Feature not implemented"


class ProtocolNotSupportedError(SocketError):
    message = "The protocol type or the specified protocol "\
              "is not supported within this domain"


class AccessError(SocketError):
    message = "Permission to create a socket "\
              "of the specified type and/or protocol is denied"


class NoFilesError(SocketError):
    message = "Process/System file table is full"


class NoBuffersError(SocketError):
    message = "Insufficient buffer space is available. "\
              "The socket cannot be created until sufficient "\
              "resources are freed."


class ConnectionRefusedError(SocketError):
    message = "Connection Refused"


class NotConnectedError(SocketError):
    message = "The socket is associated with a connection-oriented protocol "\
              "and has not been connected"


class BrokenPipeError(SocketError):
    message = "Broken pipe"


class AccessError(SocketError):
    message = "Permission Denied"


class SocketTimeoutError(SocketError):
    message = "Socket Timeout"


class AddressFamilyError(SocketError):
    message = "Address family for hostname not supported"


class TemporaryResolutionError(SocketError):
    message = "Temporary failure in name resolution"


class NonRecoverableResolutionError(SocketError):
    message = "Non-recoverable failure in name resolution"


class NameNotKnownError(SocketError):
    message = "Node name or service name not known"


class NoMemoryError(SocketError):
    message = "Memory allocation failure"


class BadFileError(SocketError):
    message = "Bad File Descriptor"


class AddressInUse(SocketError):
    message = "Address already in use"


##
## Error name to Exception class mapping
## Used to populate SOCKET_ERROR_TO_EXCEP
##
SOCKET_ERRORS = [
    ("EPERM", AccessError),
    ("EPROTONOSUPPORT", ProtocolNotSupportedError),
    ("EACCESS", AccessError),
    ("EMFILE", NoFilesError),
    ("ENFILE", NoFilesError),
    ("ENOBUFS", NoBuffersError),
    ("ECONNREFUSED", ConnectionRefusedError),
    ("ENOTCONN", NotConnectedError),
    ("EPIPE", BrokenPipeError),
    ("EACCES", AccessError),
    ("EBADF", BadFileError),
    ("EADDRINUSE", AddressInUse),
]

SOCKET_GAIERROR = [
    ("EAI_ADDRFAMILY", AddressFamilyError),
    ('EAI_AGAIN', TemporaryResolutionError),
    #('EAI_BADFLAGS',),
    ('EAI_FAIL', NonRecoverableResolutionError),
    #('EAI_FAMILY',),
    ('EAI_MEMORY', NoMemoryError),
    #('EAI_NODATA',),
    ('EAI_NONAME', NameNotKnownError),
    #('EAI_SERVICE',),
    #('EAI_SOCKTYPE',),
    #('EAI_SYSTEM',),
]
##
## socket.error to Exception class mapping
##
SOCKET_ERROR_TO_EXCEPTION = {}
for error_name, exception_class in SOCKET_ERRORS:
    try:
        c = getattr(errno, error_name)
        SOCKET_ERROR_TO_EXCEPTION[c] = exception_class
    except AttributeError:
        pass

##
## socket.gaierror to Exception class mapping
##
GAIERROR_TO_EXCEPTION = {}
for error_name, exception_class in SOCKET_GAIERROR:
    try:
        c = getattr(socket, error_name)
        GAIERROR_TO_EXCEPTION[c] = exception_class
    except AttributeError:
        pass


def get_socket_error():
    """
    Check wrether the exception was caused by socket error

    :returns: SocketException instance or None if it is not an socket error
    """
    t, v, tb = sys.exc_info()
    if not t:
        return None
    if t == socket.error:
        try:
            return SOCKET_ERROR_TO_EXCEPTION[v.args[0]]()
        except KeyError:
            return None
    elif t == socket.gaierror:
        try:
            return GAIERROR_TO_EXCEPTION[v.args[0]]()
        except KeyError:
            return None
    elif t == socket.timeout:
        return SocketTimeoutError()
    return None
