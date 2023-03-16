# ----------------------------------------------------------------------
# help command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import ast
import os
import subprocess
import argparse

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.handler import get_handler
from noc.config import config


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("command", nargs=argparse.REMAINDER, help="Show command's help")

    def handle(self, command=None, *args, **options):
        if command:
            return self.help_command(command[0])
        else:
            return self.list_commands()

    def list_commands(self):
        def is_command_file(path: str) -> bool:
            with open(path, "r") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == "Command":
                    return True
            return False

        commands = set()
        for root in config.get_customized_paths("commands"):
            for f in os.listdir(root):
                help = ""
                if f.startswith("_") or f.startswith("."):
                    continue
                elif f.endswith(".py"):
                    if not is_command_file(os.path.join(root, f)):
                        continue
                    try:
                        if root == "commands":
                            h = get_handler("noc.commands.%s" % f[:-3])
                        else:
                            h = get_handler("noc.custom.commands.%s" % f[:-3])
                        ha = getattr(h, "Command", "")
                        if ha:
                            help = ha.help
                    except Exception:
                        help = ""
                    commands.add((f[:-3], help))
                elif f.endswith(".sh"):
                    commands.add((f[:-3], help))
        for cmd in sorted(commands):
            self.print("%-20s %s" % cmd)
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
