# ----------------------------------------------------------------------
# Login debugging utility
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import getpass
import argparse

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.services.login.backends.base import BaseAuthBackend


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--backend",
            action="store",
            dest="backend",
            default="ldap",
            help="Authentication backend",
        )
        parser.add_argument("--user", action="store", dest="user", help="Username")
        parser.add_argument("--password", action="store", dest="password", help="Password")

    def handle(self, backend, user, password, *args, **kwargs):
        if not password:
            password = getpass.getpass()
        connect()
        backend = BaseAuthBackend.get_backend(backend)
        auth = backend(None)
        try:
            auth.authenticate(user=user, password=password)
        except backend.LoginError as e:
            self.die(f"Failed to login: {e}")
        self.print("Login successful")
