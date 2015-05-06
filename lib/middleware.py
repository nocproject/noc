# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## WEB Middleware Classes
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import base64
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local
## Django modules
from django.contrib import auth


class HTTPBasicAuthMiddleware(object):
    """
    Process HTTP Basic auth
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            # Already authenticated
            return
        if "HTTP_AUTHORIZATION" in request.META:
            a = request.META["HTTP_AUTHORIZATION"]
            if a.startswith("Basic "):
                username, password = base64.b64decode(a[6:]).split(":")
                user = auth.authenticate(username=username, password=password)
                if user:
                    # Authentication passed
                    request.user = user


##
## Thread local storage
##
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


class ExtFormatMiddleware(object):
    """
    Set request.is_extjs when __format=ext found in request
    """
    def process_request(self, request):
        if request.GET and request.GET.get("__format") == "ext":
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
