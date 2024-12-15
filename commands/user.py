# ---------------------------------------------------------------------
# Maintain users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import random

# NOC modules
from noc.core.management.base import BaseCommand, CommandError
from noc.aaa.models.user import User
from noc.aaa.models.permission import Permission


class Command(BaseCommand):
    help = "Manage users"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # extract command
        user_create = subparsers.add_parser("add")
        user_create.add_argument("--username", dest="username", action="store", help="User name"),
        user_create.add_argument("--email", dest="email", action="store", help="Email"),
        user_create.add_argument(
            "--template", dest="template", action="append", help="Apply template"
        ),
        user_create.add_argument(
            "--pwgen", dest="pwgen", action="store_true", help="Generate random password"
        ),

    pwset = "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "1234567890"
    PWLEN = 12

    TEMPLATES = {"probe": ["pm:probe:config"]}

    def out(self, msg):
        if not self.verbose_level:
            return
        print(msg)

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_add(self, *args, **options):
        if "username" not in options:
            raise CommandError("Username is not set")
        if "email" not in options:
            raise CommandError("Email is not set")
        if "pwgen" in options:
            passwd = "".join(random.choice(self.pwset) for _ in range(self.PWLEN))
        else:
            passwd = None
        if not passwd:
            raise CommandError("Password is not set")
        permissions = set()
        if not options.get("template"):
            raise CommandError("template permission not set")
        for t in options["template"]:
            if t not in self.TEMPLATES:
                raise CommandError("Invalid template '%s'" % t)
            permissions.update(self.TEMPLATES[t])
        if not permissions:
            raise CommandError("No permissions set")
        # Create user
        u = User(username=options["username"], email=options["email"], is_active=True)
        try:
            u.set_password(passwd, save=False)
        except ValueError as e:
            self.die(f"Cannot set password: {e.args[0]}")
        u.save()
        for p in permissions:
            try:
                perm = Permission.objects.get(name=p)
            except Permission.DoesNotExist:
                perm = Permission(name=p)
                perm.save()
            perm.users.add(u)
        print(passwd)


if __name__ == "__main__":
    Command().run()
