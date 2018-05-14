# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Login debugging utility
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
from dateutil.parser import parse
import getpass
import ldap3
# NOC modules
from noc.core.management.base import BaseCommand
from noc.main.models.authldapdomain import AuthLDAPDomain
from noc.core.management.base import BaseCommand
from noc.services.login.backends.base import BaseAuthBackend


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--backend",
            action="store",
            dest="backend",
            default="ldap",
            help="Authentication backend"
        )
        parser.add_argument(
            "--user",
            action="store",
            dest="user",
            help="Username"
        )
        parser.add_argument(
            "--password",
            action="store",
            dest="password",
            help="Password"
        )
        parser.add_argument(
            "--info",
            action="store_true",
            help="LDAP User Info"
        )

    def handle(self, backend, user, password, info=False, *args, **kwargs):
        if info:
            backend = BaseAuthBackend.get_backend(backend)
            auth = backend(None)
            ldap_domain = AuthLDAPDomain.get_default_domain()
            server_pool = auth.get_server_pool(ldap_domain)
            connect = ldap3.Connection(server_pool, user=ldap_domain.bind_user, password=ldap_domain.bind_password)
            if not connect.bind():
                self.print(
                    "Cannot bind as %s to search groups",
                    ldap_domain.bind_user
                )
                connect = None
            result = self.ad_search_by_user(connect, user, ldap_domain.root)
            for i, s in result.items():
                if "memberOf" in i:
                    s = s.replace("#", "\n")
                if "whenChanged" in i:
                    s = parse(s.split(".")[0])
                self.print("%s:%s" % (i,s))
        else:
            if not password:
                password = getpass.getpass()
            backend = BaseAuthBackend.get_backend(backend)
            auth = backend(None)
            try:
                auth.authenticate(user=user, password=password)
            except backend.LoginError as e:
                self.die("Failed to login: %s" % e)
            self.print("Login successful")

    def ad_search_by_user(self, connection, user, path_root):
        user_info = {}
        if "@" in user:
            adFltr = "(&(objectclass=user)(mail=" + user + "))"
        else:
            adFltr = "(&(objectclass=user)(sAMAccountName=" + user + "))"
        connection.search(search_base=path_root,
                          search_filter=adFltr,
                          search_scope=ldap3.SUBTREE,
                          attributes=["displayName",
                                      "sAMAccountName",
                                      "memberOf",
                                      "whenChanged",
                                      "mail",
                                      "distinguishedName"],
                          size_limit=0)
        entry = connection.entries[0]
        attrs = entry.entry_get_attributes_dict()
        for k, v in attrs.items():
            if k in attrs:
                value = attrs[k]
                if isinstance(value, (list, tuple)):
                    value = "#".join(value)
                user_info[k] = value
        return user_info

if __name__ == "__main__":
    Command().run()
