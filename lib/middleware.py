# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# WEB Middleware Classes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local
# Django modules

#
# Thread local storage
#
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


class WSGISetupMiddleware(object):
    """
    Set up WSGI headers
    """

    def process_request(self, request):
        ru = request.META.get("HTTP_REMOTE_USER")
        if ru:
            request.META["REMOTE_USER"] = ru


class ExtFormatMiddleware(object):
    """
    Set request.is_extjs when __format=ext found in request
    """

    def process_request(self, request):
        if request.GET and request.GET.get("__format") == "ext":
            request.is_extjs = True
        elif request.POST and request.POST.get("__format") == "ext":
            request.is_extjs = True
        else:
            request.is_extjs = False


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
