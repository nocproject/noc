# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# help command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import os
import subprocess
import argparse
# NOC modules
from noc.core.management.base import BaseCommand
from noc.config import config


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "command",
            nargs=argparse.REMAINDER,
            help="Show command's help"
        )

    def handle(self, command=None, *args, **options):
        if command:
            return self.help_command(command[0])
        else:
            return self.list_commands()

    def list_commands(self):
        commands = set()
        for root in config.get_customized_paths("commands"):
            for f in os.listdir(root):
                if f.startswith("_") or f.startswith("."):
                    continue
                if f.endswith(".py") or f.endswith(".sh"):
                    commands.add(f[:-3])
        for cmd in sorted(commands):
            self.print(cmd)
        return 0

    def help_command(self, cmd):
        for root in config.get_customized_paths("commands"):
            # Python, call help
            path = os.path.join(root, "%s.py" % cmd)
            if os.path.exists(path):
                return subprocess.call([os.environ.get("NOC_CMD", "./noc"), cmd, "--help"])
            # Shell, no help
            path = os.path.join(root, "%s.sh" % cmd)
            if os.path.exists(path):
                self.print("Help is not available for '%s'" % cmd)
                return 1
        # Command not found
        self.print("Unknown command '%s'" % cmd)
        return 1


if __name__ == "__main__":
    Command().run()
