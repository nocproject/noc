# ----------------------------------------------------------------------
# Test framework
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import time
import argparse
import sys

# Third-party modules
from pytest import main as pytest_main

# NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # Run
        run_parser = subparsers.add_parser("run")
        run_parser.add_argument("-v", "--verbose", action="count", help="Verbose output")
        run_parser.add_argument(
            "--test-db", help="Test database name", default=os.environ.get("NOC_TEST_DB")
        )
        run_parser.add_argument(
            "--coverage-report", help="Write coverage report to specified directory"
        )
        run_parser.add_argument("--junit-report", help="Write JUnit XML report to specified file")
        run_parser.add_argument("--idea-bookmarks", help="Dump warnings as IDEA bookmarks XML")
        run_parser.add_argument("--statistics", action="store_true", help="Dump statistics")
        run_parser.add_argument("tests", nargs=argparse.REMAINDER, help="Paths to tests")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_check(self, check_cmd, *args, **options):
        return getattr(self, "handle_check_%s" % check_cmd)(*args, **options)

    def handle_run(
        self,
        tests=None,
        verbose=False,
        test_db=None,
        statistics=False,
        coverage_report=None,
        junit_report=None,
        idea_bookmarks=None,
        *args,
        **options,
    ):
        def run_tests(args):
            self.print("Running test")
            # Must be imported within coverage
            from noc.core.ioloop.util import setup_asyncio

            setup_asyncio()
            from noc.config import config

            if test_db:
                db_name = test_db
            else:
                db_name = "test_%d" % time.time()  # Generate unique database name
            # Override database names
            config.pg.db = db_name
            config.mongo.db = db_name
            config.clickhouse.db = db_name
            exit_code = pytest_main(args)
            if idea_bookmarks:
                self.dump_idea_bookmarks(idea_bookmarks)
            return exit_code

        # Run tests
        args = ["--maxfail", 2]
        if verbose:
            args += ["-" + ("v" * verbose)]
        if junit_report:
            args += ["--junitxml", junit_report]
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
        from coverage.misc import NoSource
        from noc.tests.conftest import _stats as stats

        self.print("---[ Test session statistics ]------")
        cov_data = cov.get_data()
        totals = Numbers()
        for fr in cov_data.measured_files():
            try:
                analysis = cov._analyze(fr)
            except NoSource:
                continue
            totals += analysis.numbers
        n_passed = len(stats.get("passed", []))
        n_skipped = len(stats.get("skipped", []))
        n_error = len(stats.get("error", []))
        n_failed = len(stats.get("failed", []))
        n_xfailed = len(stats.get("xfailed", []))
        n_xpassed = len(stats.get("xpassed", []))
        n_warnings = len(stats.get("warnings", []))
        if n_error or n_failed:
            status = "Failed"
        else:
            status = "Passed"
        self.print("Status              : %s" % status)
        self.print("Tests Passed:       : %s" % n_passed)
        self.print("Tests Skipped:      : %s" % n_skipped)
        self.print("Tests Failed:       : %s" % n_failed)
        self.print("Tests Error:        : %s" % n_error)
        self.print("Tests XFailed       : %s" % n_xfailed)
        self.print("Tests XPassed       : %s" % n_xpassed)
        self.print("Tests Warnings      : %s" % n_warnings)
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

    def dump_idea_bookmarks(self, path):
        def is_project_path(p):
            return os.path.commonprefix([cwd, p]) == cwd

        from noc.tests.conftest import _stats as stats

        warnings = stats.get("warnings", [])
        r = []
        cwd = os.path.abspath(os.getcwd())
        lcwd = len(cwd)
        if not cwd.endswith(os.sep):
            lcwd += len(os.sep)
        for w in warnings:
            wp, line = w.fslocation
            if is_project_path(wp):
                r += [
                    '<bookmark url="file://$PROJECT_DIR$/%s" line="%d" />' % (wp[lcwd:], line - 1)
                ]
        if not r:
            self.print("No warnings to dump as bookmarks")
            return
        self.print("Dumping %d IDEA bookmarks to %s" % (len(r), path))
        with open(path, "w") as f:
            f.write("\n".join(sorted(r)))


if __name__ == "__main__":
    Command().run()
