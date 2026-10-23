# ---------------------------------------------------------------------
# TLS Middleware
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import local

# Thread local storage
_tls = local()


def tls_middleware(get_response):
    """
    Store request and user to thread-local storage

    :param get_response: Callable returning response from downstream middleware
    :return:
    """

    def middleware(request):
        global _tls

        _tls.request = request
        set_user(getattr(request, "user", None))
        response = get_response(request)
        _tls.request = None
        _tls.user = None
        return response

    return middleware


def set_user(user):
    """
    Set up TLS user
    """
    _tls.user = user


def get_user():
    """
    Get current TLS user
    """
    return getattr(_tls, "user", None)


def get_request():
    """
    Get current TLS request
    """
    return getattr(_tls, "request", None)
