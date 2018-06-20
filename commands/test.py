# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test framework
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import os
import subprocess
import time
import argparse
import sys
# Third-party modules
from pytest import main as pytest_main
# NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # Run
        run_parser = subparsers.add_parser("run")
        run_parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Verbose output"
        )
        run_parser.add_argument(
            "--coverage-report",
            help="Write coverage report to specified directory"
        )
        run_parser.add_argument(
            "--test-report",
            help="Write HTML error report to specified path"
        )
        run_parser.add_argument(
            "tests",
            nargs=argparse.REMAINDER,
            help="Paths to tests"
        )
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
        from noc.config import config
        dirs = self.get_dirs(config.tests.events_path)
        if pull:
            self.pull_repos(dirs)
        return pytest_main(["tests/test_eventclassificationrule.py"])

    def handle_check_profilecheckrule(self, *args, **options):
        raise NotImplementedError()

    def handle_check_script(self, *args, **options):
        raise NotImplementedError()

    def handle_run(self, tests=None, verbose=False, coverage_report=False,
                   test_report=None, *args, **options):
        def run_tests(args):
            self.print("Running test")
            # Must be imported within coverage
            from noc.config import config
            db_name = "test_%d" % time.time()
            # Override database names
            config.pg.db = db_name
            config.mongo.db = db_name
            config.clickhouse.db = db_name
            return pytest_main(args)

        # Run tests
        args = []
        if verbose:
            args += ["-v"]
        if test_report:
            args += [
                "--html=%s" % test_report,
                "--self-contained-html"
            ]
        if tests:
            args += tests
        else:
            args += ["tests"]
        if coverage_report:
            self.print("Collecting coverage")
            # Reset all loaded modules to return them to coverage
            already_loaded = [m for m in sys.modules if m.startswith("noc.")]
            for m in already_loaded:
                del sys.modules[m]
            import coverage
            cov = coverage.Coverage()
            cov.start()
            try:
                return run_tests(args)
            finally:
                self.print("Writing coverage report to %s/index.html" % coverage_report)
                cov.stop()
                cov.save()
                cov.html_report(directory=coverage_report)
        else:
            return run_tests(args)

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
