# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# manage.py todos
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
# Third-party modules
from django.core.management.base import BaseCommand
# NOC modules
from noc.settings import INSTALLED_APPS
from noc.core.fileutils import read_file


class Command(BaseCommand):
    help = "Display todo's left in code"
    exclude = set(["main/management/commands/todos.py"])

    def handle(self, *args, **options):
        dirs = ["lib"] + [a[4:] for a in INSTALLED_APPS if a.startswith("noc.")]
        n = 0
        for d in dirs:
            for dirpath, dirs, files in os.walk(d):
                for f in files:
                    if f.startswith(".") or not f.endswith(".py"):
                        continue
                    path = os.path.join(dirpath, f)
                    if path not in self.exclude:
                        n += self.show_todos(path)
        if n:
            print "-" * 72
            print "%d todos found" % n
        else:
            print "No todos found"

    def show_todos(self, path):
        """
        Display todos
        :param path:
        :return:
        """
        data = read_file(path)
        if not data:
            return 0
        n = 0
        for nl, l in enumerate(data.splitlines()):
            if "@todo:" in l:
                idx = l.index("@todo:")
                todo = l[idx + 6:].strip()
                print "%50s:%5d: %s" % (path, nl, todo)
                n += 1
        return n
