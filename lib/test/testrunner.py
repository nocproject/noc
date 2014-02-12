# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test code runner with Coverage
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
import unittest
import logging
import types
import ConfigParser
## Django modules
from django.utils import unittest  # unittest2 backport
from django.conf import settings
from django.test import _doctest as doctest
from django.test.testcases import OutputChecker, DocTestRunner, TestCase
from django.core import management
## Third-party modules
from south.logger import get_logger
## NOC modules
import noc.settings
from testresult import NOCTestResult
from importtestcase import ImportTestCase
from coveragecontext import CoverageContext
from databasecontext import DatabaseContext
from testenvironmentcontext import TestEnvironmentContext
from beeftestcase import BeefTestCase


class TestRunner(object):
    """
    Testing engine
    """
    exclude_modules = ["noc.main.pyrules.", "noc.main.templates.", "noc.setup"]

    def __init__(self, test_labels, verbosity=1, interactive=True,
                 extra_tests=[], reuse_db=False,
                 junit_xml_out=None, coverage_xml_out=None,
                 coverage_html_out=None, fixed_beef_base=None,
                 beef=None, beef_filter=None):
        self.test_labels = test_labels
        self.verbosity = verbosity
        self.loglevel = logging.DEBUG if self.verbosity > 1 else logging.INFO
        self.interactive = interactive
        self.extra_tests = extra_tests
        self.reuse_db = reuse_db
        self.result = None
        self.coverage_report = []  # List of files to report coverage
        self.junit_xml_out = junit_xml_out
        self.coverage_xml_out = coverage_xml_out
        self.coverage_html_out = coverage_html_out
        if fixed_beef_base:
            noc.settings.TEST_FIXED_BEEF_BASE = fixed_beef_base
        self.beef = beef or self.get_beef_paths()
        self.beef_filter = beef_filter

    def info(self, message):
        logging.info(message)

    def debug(self, message):
        logging.debug(message)

    def error(self, message):
        logging.error(message)

    def coverage(self):
        """
        Get coverage context
        """
        return CoverageContext(self, xml_out=self.coverage_xml_out,
                               html_out=self.coverage_html_out)

    def databases(self, reuse=False):
        """
        Get databases context
        """
        return DatabaseContext(self, reuse=reuse, interactive=self.interactive,
                               verbosity=self.verbosity)

    def test_environment(self):
        """
        Get test environment context
        """
        return TestEnvironmentContext()

    def get_manifest(self):
        """
        Generate a list of all python modules (file paths)
        """
        manifest = []
        # Root directory *.py
        manifest += [f for f in os.listdir(".")
                     if os.path.splitext(f)[1] == ".py" and f != "__init__.py"]
        dirs = (["lib", "tests"] +
                [app[4:] for app in settings.INSTALLED_APPS
                 if app.startswith("noc.")])
        for top in dirs:
            for root, dirs, files in os.walk(top):
                parts = root.split(os.sep)
                if len(parts) > 1 and parts[1] in ("migrations", "management"):
                    continue
                manifest += [os.path.join(root, f) for f in files
                             if (not f.startswith(".") and
                                os.path.splitext(f)[1] == ".py")]
        return manifest

    def get_modules(self, test_labels):
        """
        Get modules for test suite
        """
        def path_to_mod(path):
            """
            >>> path_to_mod("lib/test_runner.py")
            'noc.lib.test_runner'
            >>> path_to_mod("sa/profiles/__init__.py")
            'noc.sa.profiles'
            """
            if os.path.splitext(path)[1] == ".py":
                path = path[:-3]
            m = ["noc"] + path.split(os.path.sep)
            if m[-1] == "__init__":
                m = m[:-1]
            return ".".join(m)

        def mod_to_path(mod):
            """
            >>> mod_to_path("noc.lib.test_runner")
            'lib/test_runner.py'
            >>> mod_to_path("noc.sa.profiles")
            'sa/profiles/__init__.py'
            """
            if mod.startswith("noc."):
                mod = mod[4:]
            path = mod.replace(".", os.path.sep)
            if os.path.isdir(path):
                path = os.path.join(path, "__init__")
            return path + ".py"

        def is_match(module, labels):
            """ Check module matches test label """
            parts = module.split(".")
            lp = len(parts)
            for l in labels:
                ll = len(l)
                if lp >= ll and parts[:ll] == l:
                    return True
            return False

        def to_exclude(module):
            for x in self.exclude_modules:
                if module.startswith(x):
                    return True
            return False

        # Build files manifest
        manifest = [path_to_mod(p) for p in self.get_manifest()]
        if test_labels:
            # Filter modules
            l = [tl.split(".") for tl in test_labels]
            manifest = [m for m in manifest if is_match(m, l)]
        # Exclude modules
        manifest = [m for m in manifest if not to_exclude(m)]
        # Coverate report manifest
        self.coverage_report = [mod_to_path(m) for m in manifest]
        # Get unittests and modules
        tests = [f for f in manifest if "tests" in f.split(".")[:-1]]
        st = set(tests)
        modules = [f for f in manifest if f not in st]
        n_unittests = len(tests)
        n_mods = len(modules)
        self.info("Found: %d unittest modules, %d python modules" % (
            n_unittests, n_mods))
        return modules, tests

    def get_beef_paths(self):
        r = []
        config = ConfigParser.SafeConfigParser()
        config.read("etc/beef.defaults")
        config.read("etc/beef.conf")
        for s in config.sections():
            if (config.getboolean(s, "enabled") and
                config.get(s, "type") == "sa"):
                r += ["local/repos/sa/%s/" % s]
        return r

    def get_beef(self, path):
        r = []
        for prefix, dirnames, filenames in os.walk(path):
            for f in filenames:
                if f.endswith(".json"):
                    p = os.path.join(prefix, f)
                    tc = BeefTestCase()
                    tc.load_beef(p)
                    if self.beef_filter:
                        for f in self.beef_filter:
                            if tc.guid == f or tc.script.startswith(f):
                                r += [tc]
                                break
                    else:
                        r += [tc]
        return r

    def get_suite(self, modules, tests):
        # Prepare suite
        suite = unittest.TestSuite()
        # Add import tests
        suite.addTests([ImportTestCase(m) for m in modules])
        # Add doctests
        output_checker = OutputChecker()
        for m in modules:
            try:
                suite.addTests(doctest.DocTestSuite(m, checker=output_checker,
                                                    runner=DocTestRunner))
            except ValueError:
                # No tests
                continue
        # Add unittests
        for m in tests:
            try:
                mo = __import__(m, {}, {}, "*")
            except (ImportError, AssertionError):
                suite.addTest(ImportTestCase(m))
                continue
            t = []
            for name in dir(mo):
                obj = getattr(mo, name)
                if (isinstance(obj, (type, types.ClassType)) and
                    issubclass(obj, unittest.TestCase)):
                    if obj.__module__ == m:
                        t += [unittest.defaultTestLoader.loadTestsFromTestCase(obj)]
            suite.addTest(unittest.TestSuite(t))
        # Add beef tests
        for path in self.beef:
            suite.addTests(self.get_beef(path))
        self.info("Test suite build: %d test cases are found" % suite.countTestCases())
        return suite

    def run(self):
        """
        Set up environment and run tests.
        Returns number of errors
        """
        # Set up south logger
        get_logger().setLevel(self.loglevel)
        # Set up system logger
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s %(message)s")
        # Prepare environment and run tests
        with self.test_environment():
            # Get test suite
            modules, tests = self.get_modules(self.test_labels)
            # Check modules are found
            if len(modules) == 0 and len(tests) == 0:
                if self.beef:
                    self.reuse_db = True
                else:
                    self.info("No modules to test. Exiting")
                    return 0
            # Run test suite in database and coverage context
            with self.coverage():
                with self.databases(reuse=self.reuse_db):
                    # Initialize database: Wrap as tests
                    if not self.reuse_db:
                        management.call_command("sync-perm")
                        #management.call_command("sync-pyrules")
                        management.call_command("collection --sync")
                        management.call_command("beef", "--pull")
                    # Add as tests
                    suite = self.get_suite(modules, tests)
                    self.info("Running test suite")
                    runner = unittest.TextTestRunner(verbosity=self.verbosity,
                                                     resultclass=NOCTestResult)
                    self.result = runner.run(suite)
                    self.info("Test suite completed")
        # Return summary
        if self.result:
            if self.junit_xml_out:
                self.result.write_xml(self.junit_xml_out)
            else:
                self.result.dump_result()
            return len(self.result.failures) + len(self.result.errors)
        else:
            return 1
