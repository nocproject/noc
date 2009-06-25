# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## WEB Middleware Classes
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local
##
## Thread local storage
##
_tls=local()

##
## Thread Local Storage Middleware
##
class TLSMiddleware(object):
    ## Fill TLS
    def process_request(self,request):
        _tls.request=request
        _tls.user=getattr(request,"user",None)
    # Clean TLS
    def process_response(self,request,response):
        _tls.request=None
        _tls.user=None
        return response
    # Clean TLS
    def process_exception(self,request,exception):
        _tls.request=None
        _tls.user=None
##
## Returns current user
##
def get_user():
    return getattr(_tls,"user",None)
##
## Returns current request
##
def get_request():
    return getattr(_tls,"request",None)
