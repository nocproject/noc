# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LDAP Authentication backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import ldap3
## NOC modules
from base import BaseAuthBackend


class LdapBackend(BaseAuthBackend):
    def authenticate(self, user=None, password=None, **kwargs):
        ldap_server = self.service.config.ldap_server
        if "," in ldap_server:
            ldap_server = [x.strip() for x in ldap_server.split(",")]

        connect = ldap3.Connection(
            ldap_server,
            user=user,
            password=password
        )
        if not connect.bind():
            raise self.LoginError(
                "Failed to bind to LDAP: %s",
                connect.result
            )
