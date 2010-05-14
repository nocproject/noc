# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test code runner with Coverage
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import os,unittest,sys
from django.test import simple
from django.conf import settings
from django.test.utils import setup_test_environment, teardown_test_environment
from coverage import coverage as Coverage
from django.test import _doctest as doctest
from django.test.testcases import OutputChecker, DocTestRunner, TestCase
##
## Test module by importing it
##
class ImportTestCase(unittest.TestCase):
    def __init__(self,module):
        super(ImportTestCase,self).__init__()
        self.module=module
    def runTest(self):
        __import__(self.module,{},{},"*")
##
## Generator returning NOC's modules
##
def get_modules():
    for app in settings.INSTALLED_APPS:
        if not app.startswith("noc."):
            # Skip all contributed apps
            continue
        n,d=app.split(".")
        yield d
##
## Return test modules from below path
##
def get_test_suite(path):
    for root,dirs,files in os.walk(path):
        for f in [f for f in files if f.endswith(".py")]:
            yield ".".join(["noc"]+root.split(os.path.sep)+[f[:-3]])
##
## Build module list for Coverage
## and application test suite
##
def get_tests(test_labels):
    modules=["urls.py","settings.py"]
    suite=[]
    # Add additional test libraries
    for d in ["","lib"]:
        p=os.path.join(d,"tests")
        if os.path.isdir(p):
            suite+=list(get_test_suite(p))
    # Scan modules for tests
    for d in get_modules():
        # Add module's tests/
        td=os.path.join(d,"tests")
        if os.path.isdir(td):
            suite+=list(get_test_suite(td))
        #
        for root,dirs,files in os.walk(d):
            parts=root.split(os.path.sep)
            if "migrations" in parts: # Skip migrations
                continue
            if "tests" not in parts:
                modules+=[m for m in [os.path.join(root,f) for f in files if f.endswith(".py")] if os.path.getsize(m)>1]
            # Add all tests from applications's tests/
            if len(parts)==4 and parts[1]=="apps" and parts[3]=="tests":
                suite+=list(get_test_suite(root))
            # Add all applications tests.py
            if len(parts)==3 and parts[1]=="apps" and "tests.py" in files:
                mn=".".join(["noc"]+parts+["tests"])
                suite+=[mn]
    ## Scan lib/ for tests
    for root,dirs,files in os.walk("lib"):
        if "tests" in root:
            continue
        modules+=[m for m in [os.path.join(root,f) for f in files if f.endswith(".py")] if os.path.getsize(m)>1]
    return modules,suite
##
## "manage.py test" runner
##
def run_tests(test_labels,verbosity=1,interactive=True,extra_tests=[],coverage=True,reuse_db=False):
    def match_test(m):
        if not test_labels:
            return True
        for l in test_labels:
            if m.startswith(l):
                return True
        return False
    # Mark testing environment
    settings.NOC_TEST=True
    suite=unittest.TestSuite()
    # Scan for tests
    print "Scanning for tests ...",
    modules,tsuite=get_tests(test_labels)
    print "... %d test cases found"%(len(modules)+len(tsuite))
    print "Preparing test cases ..."
    if coverage:
        coverage=Coverage()
        coverage.exclude(r"^\s*$")                # Exclude empty lines
        coverage.exclude(r"^\s*#.*$")             # Exclude comment blocks
        coverage.exclude(r"^\s*(import|from)\s")  # Exclude import statements
        # Run tests
        coverage.start()
    # Add docstrings and module load tests
    # Run inside Coverage context
    doctestOutputChecker = OutputChecker()
    for m in modules:
        mn="noc."+m.replace(os.path.sep,".")[:-3]
        if mn.endswith("__init__"):
            mn=mn[:-9]
        if match_test(mn):
            # Module load
            suite.addTest(ImportTestCase(mn))
            # Docstrings
            try:
                suite.addTest(doctest.DocTestSuite(mn,checker=doctestOutputChecker,runner=DocTestRunner))
            except ValueError:
                pass # No doctests in module
    for m in tsuite:
        if not match_test(m):
            continue
        mo=__import__(m,{},{},"*")
        suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(mo))
    for test in extra_tests:
        suite.addTest(test)
    # Run tests
    print "Testing ..."
    setup_test_environment()
    settings.DEBUG = False
    old_name = settings.DATABASE_NAME
    from django.db import connection
    try:
        connection.cursor() # Raises operational error when no database exists
        has_db=True
    except:
        has_db=False
    # Create database when necessary
    if not reuse_db or not has_db:
        connection.creation.create_test_db(verbosity, autoclobber=not interactive)
    # Run tests
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    # Drop database when necessary
    if not reuse_db:
        connection.creation.destroy_test_db(old_name, verbosity)
    teardown_test_environment()

    test_results=len(result.failures) + len(result.errors)
    if coverage:
        coverage.stop()
        # Coverage HTML Report
        print "Writing Coverage report to %s"%settings.COVERAGE_REPORT_PATH
        coverage.html_report(modules, directory=settings.COVERAGE_REPORT_PATH)
        print "Done"
    return test_results
