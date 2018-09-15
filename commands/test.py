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
            action="count",
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
            "--statistics",
            action="store_true",
            help="Dump statistics"
        )
        run_parser.add_argument(
            "tests",
            nargs=argparse.REMAINDER,
            help="Paths to tests"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_check(self, check_cmd, *args, **options):
        return getattr(self, "handle_check_%s" % check_cmd)(*args, **options)

    def handle_run(self, tests=None, verbose=False, statistics=False,
                   coverage_report=False, test_report=None, *args, **options):
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
            args += ["-" + ("v" * verbose)]
        if test_report:
            args += [
                "--html=%s" % test_report,
                "--self-contained-html"
            ]
        if tests:
            args += tests
        else:
            args += ["tests"]
        if statistics or coverage_report:
            self.print("Collecting coverage")
            # Reset all loaded modules to return them to coverage
            already_loaded = [m for m in sys.modules if m.startswith("noc.")]
            for m in already_loaded:
                del sys.modules[m]
            import coverage
            cov = coverage.Coverage()
            cov.start()
            try:
                result = run_tests(args)
            finally:
                if coverage_report:
                    self.print("Writing coverage report to %s/index.html" % coverage_report)
                cov.stop()
                cov.save()
                if coverage_report:
                    cov.html_report(directory=coverage_report)
                if statistics:
                    self.dump_failed()
                    self.dump_statistics(cov)
            return result
        else:
            return run_tests(args)

    def dump_statistics(self, cov):
        """
        Dump test run statistics
        :param cov:
        :return:
        """
        from coverage.results import Numbers
        from coverage.report import Reporter
        from noc.tests.conftest import _stats as stats

        self.print("---[ Test session statistics ]------")
        cov.get_data()
        reporter = Reporter(cov, cov.config)
        totals = Numbers()
        for fr in reporter.find_file_reporters(None):
            analysis = cov._analyze(fr)
            totals += analysis.numbers
        n_passed = len(stats.get("passed", []))
        n_skipped = len(stats.get("skipped", []))
        n_error = len(stats.get("error", []))
        n_failed = len(stats.get("failed", []))
        if n_error or n_failed:
            status = "Failed"
        else:
            status = "Passed"
        self.print("Status              : %s" % status)
        self.print("Tests Passed:       : %s" % n_passed)
        self.print("Tests Skipped:      : %s" % n_skipped)
        self.print("Tests Failed:       : %s" % n_failed)
        self.print("Tests Error:        : %s" % n_error)
        self.print("Coverage            : %d%%" % totals.pc_covered)
        self.print("Coverage Statements : %s" % totals.n_statements)
        self.print("Coverage Missing    : %s" % totals.n_missing)
        self.print("Coverage Excluded   : %s" % totals.n_excluded)

    def dump_failed(self):
        """
        Dump failed tests list
        :return:
        """
        from noc.tests.conftest import _stats as stats
        failed = sorted(tr.nodeid for tr in stats.get("failed", []))
        if not failed:
            return
        self.print("---[ Failed tests ]------")
        self.print("\n".join(failed))

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
