# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Login debugging utility
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import getpass
# NOC modules
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

    def handle(self, backend, user, password, *args, **kwargs):
        if not password:
            password = getpass.getpass()
        backend = BaseAuthBackend.get_backend(backend)
        auth = backend(None)
        try:
            auth.authenticate(user=user, password=password)
        except backend.LoginError as e:
            self.die("Failed to login: %s" % e)
        self.print("Login successful")

if __name__ == "__main__":
    Command().run()
