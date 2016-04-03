# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Authentication Backends
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

class BaseAuthBackend(object):
    class LoginError(Exception):
        pass

    def __init__(self, service):
        self.service = service

    def authenticate(self, **kwargs):
        """
        Authenticate user using given credentials.
        Raise LoginError when failed
        """
        raise self.LoginError()
