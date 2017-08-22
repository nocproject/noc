# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  Test framework
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import sys
import re
import os
import subprocess
# Third-party modules
from pytest import main as pytest_main
# NOC modules
from noc.core.management.base import BaseCommand
from noc.config import config


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # Run
        run_parser = subparsers.add_parser("run")
        # Check
        check_parser = subparsers.add_parser("check")
        check_cmd_parser = check_parser.add_subparsers(dest="check_cmd")
        ecr_parser = check_cmd_parser.add_parser("eventclassificationrule")
        ecr_parser.add_argument(
            "--pull",
            action="store_true",
            help="Pull repo before check"
        )
        check_cmd_parser.add_parser("profilecheckrule")
        check_cmd_parser.add_parser("script")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_check(self, check_cmd, *args, **options):
        return getattr(self, "handle_check_%s" % check_cmd)(*args, **options)

    def handle_check_eventclassificationrule(self, pull=False,
                                             *args, **options):
        dirs = self.get_dirs(config.tests.events_path)
        if pull:
            self.pull_repos(dirs)
        return pytest_main(["tests/test_eventclassificationrule.py"])

    def handle_check_profilecheckrule(self, *args, **options):
        raise NotImplementedError()

    def handle_check_script(self, *args, **options):
        raise NotImplementedError()

    def handle_run(self, *args, **options):
        return pytest_main(["tests"])

    def get_dirs(self, dirs):
        """
        Return existent directories
        :param dirs:
        :return:
        """
        return [d for d in dirs if d and os.path.isdir(d)]

    def pull_repos(self, dirs):
        """
        Pull each git repo from directory
        :param dirs:
        :return:
        """
        for d in dirs:
            if os.path.isdir(os.path.join(d, ".git")):
                self.print("Pulling %s" % d)
                subprocess.check_call(["git", "pull"], cwd=d)
        else:
            self.print("No directories to pull")

if __name__ == "__main__":
    Command().run()
