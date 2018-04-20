# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Maintain users
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import make_option
import random
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.main.models import User
from noc.main.models.permission import Permission


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Manage Full-Text Search index"
    option_list=BaseCommand.option_list+(
        make_option(
            "--add", "-a",
            action="store_const",
            dest="cmd",
            const="add",
            help="Create user"
        ),
        make_option(
            "--username",
            action="store",
            dest="username",
            help="User name"
        ),
        make_option(
            "--email",
            action="store",
            dest="email",
            help="Email"
        ),
        make_option(
            "--template",
            action="append",
            dest="template",
            help="Apply template"
        ),
        make_option(
            "--pwgen",
            action="store_true",
            dest="pwgen",
            help="Generate random password"
        )
    )

    pwset = "abcdefghijklmnopqrstuvwxyz" \
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
            "1234567890"
    PWLEN = 12

    TEMPLATES = {
        "probe": [
            "pm:probe:config"
        ]
    }

    def out(self, msg):
        if not self.verbose:
            return
        print msg

    def handle(self, *args, **options):
        if options["cmd"] == "add":
            self.handle_add(*args, **options)

    def handle_add(self, *args, **options):
        if not options["username"]:
            raise CommandError("Username is not set")
        if not options["email"]:
            raise CommandError("Email is not set")
        if options["pwgen"]:
            passwd = "".join(random.choice(self.pwset)
                             for _ in range(self.PWLEN))
        else:
            passwd = None
        if not passwd:
            raise CommandError("Password is not set")
        permissions = set()
        for t in options["template"]:
            if t not in self.TEMPLATES:
                raise CommandError("Invalid template '%s'" % t)
            permissions.update(self.TEMPLATES[t])
        if not permissions:
            raise CommandError("No permissions set")
        # Create user
        u = User(
            username=options["username"],
            email=options["email"],
            is_active=True
        )
        u.set_password(passwd)
        u.save()
        for p in permissions:
            try:
                perm = Permission.objects.get(name=p)
            except Permission.DoesNotExist:
                perm = Permission(name=p)
                perm.save()
            perm.users.add(u)
        print passwd
