# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PyRule Authentication backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from base import NOCAuthBackend
from noc.settings import config

## @todo: fix
class NOCPyRuleBackend(NOCAuthBackend):
    def authenticate(self,**kwargs):
        try:
            return PyRule.call(settings.AUTH_PYRULE_AUTHENTICATION,**kwargs)
        except Exception,why:
            logging.error("PyRule backend exception: %s"%str(why))