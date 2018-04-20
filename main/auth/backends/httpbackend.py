# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HTTP Authentication backend
## Trust REMOTE_USER
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import NOCAuthBackend


class NOCHTTPBackend(NOCAuthBackend):
    """
    Trust REMOTE_USER environment variable passed by HTTP server
    """
    def authenticate(self, remote_user, **kwargs):
        if not remote_user:
            return None
        return self.get_or_create_db_user(username=remote_user, is_active=True)
