# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PyRule Authentication backend
## Trust REMOTE_USER
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from noc.main.models import PyRule
import settings,logging

class NOCPyRuleBackend(ModelBackend):
    def authenticate(self,**kwargs):
        try:
            return PyRule.call(settings.AUTH_PYRULE_AUTHENTICATION,**kwargs)
        except Exception,why:
            logging.error("PyRule backend exception: %s"%str(why))