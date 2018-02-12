# -*- coding: utf-8 -*-
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


class TLSMiddleware(object):
    """
    Thread local storage middleware
    """
    def process_request(self, request):
        """
        Set up TLS' user and request
        """
        _tls.request = request
        set_user(getattr(request, "user", None))

    def process_response(self, request, response):
        """
        Clean TLS
        """
        _tls.request = None
        _tls.user = None
        return response

    def process_exception(self, request, exception):
        """
        Clean TLS
        """
        _tls.request = None
        _tls.user = None


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
