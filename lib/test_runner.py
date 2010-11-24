# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test code runner with Coverage
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import os,unittest,sys,logging
from django.test import simple
from django.conf import settings
from django.test.utils import setup_test_environment, teardown_test_environment
from coverage import coverage as Coverage
from django.test import _doctest as doctest
from django.test.testcases import OutputChecker, DocTestRunner, TestCase
from django.core import management
from south.logger import get_logger
import types,unittest
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
## Convert path to module name
##
def path_to_mod(path):
    """
    >>> path_to_mod("lib/test_runner.py")
    'noc.lib.test_runner'
    >>> path_to_mod("sa/profiles/__init__.py")
    'noc.sa.profiles'
    """
    if path.endswith(".py"):
        path=path[:-3]
    m="noc."+path.replace(os.path.sep,".")
    if m.endswith(".__init__"):
        m=m[:-9]
    return m
##
## Convert module to path
##
def mod_to_path(mod):
    """
    >>> mod_to_path("noc.lib.test_runner")
    'lib/test_runner.py'
    >>> mod_to_path("noc.sa.profiles")
    'sa/profiles/__init__.py'
    """
    if mod.startswith("noc."):
        mod=mod[4:]
    path=mod.replace(".",os.path.sep)
    if os.path.isdir(path):
        path=os.path.join(path,"__init__")
    return path+".py"
##
## Check module matches test_labels
##
def match_test(test_labels,m):
    if m.startswith("noc.main.pyrules."):
        # Exclude built-in pyrules
        return False
    if not test_labels:
        return True
    for l in test_labels:
        if m.startswith(l):
            return True
    return False
##
## Generator returning NOC's modules
##
def get_modules():
    for app in [app for app in settings.INSTALLED_APPS if app.startswith("noc.")]:
        n,d=app.split(".")
        yield d
##
## Return test modules from below path
##
def get_test_suite(path):
    r=[]
    for root,dirs,files in os.walk(path):
        for f in [f for f in files if f.endswith(".py")]:
            r+=[path_to_mod(os.path.join(root,f))]
    return r
##
## Build module list for Coverage
## and application test suite
##
def get_tests(test_labels):
    modules=["urls","settings"]
    suite=[]
    # Add additional test libraries
    for d in ["","lib"]:
        p=os.path.join(d,"tests")
        if os.path.isdir(p):
            suite+=get_test_suite(p)
    # Scan lib/ for modules
    for root,dirs,files in os.walk("lib"):
        parts=root.split(os.path.sep)
        if "tests" in parts:
            continue
        modules+=[path_to_mod(p) for p in [os.path.join(root,f) for f in files if f.endswith(".py")] if os.path.getsize(p)>1]
    # Scan modules for tests
    for d in get_modules():
        # Add module's tests/
        td=os.path.join(d,"tests")
        if os.path.isdir(td):
            suite+=get_test_suite(td)
        # Walk for application's tests
        for root,dirs,files in os.walk(d):
            parts=root.split(os.path.sep)
            # Skip migrations
            if "migrations" in parts:
                continue
            if "tests" not in parts:
                # Add modules for import and docstring testings
                modules+=[path_to_mod(p) for p in [os.path.join(root,f) for f in files if f.endswith(".py")] if os.path.getsize(p)>1]
            # Add all tests from applications's tests/
            elif len(parts)==4 and parts[1]=="apps" and parts[3]=="tests":
                suite+=get_test_suite(root)
            # Add all applications tests.py
            elif len(parts)==3 and parts[1]=="apps" and "tests.py" in files:
                suite+=[".".join(["noc"]+parts+["tests"])]
            # Add all profile scripts tests
            elif len(parts)==5 and parts[:2]==["sa","profiles"] and parts[4]=="tests":
                suite+=get_test_suite(root)
    # Filter out
    modules=[m for m in modules if match_test(test_labels,m)]
    suite=[m for m in suite if match_test(test_labels,m)]
    return modules,suite
##
## "manage.py test" runner
##
def run_tests(test_labels,verbosity=1,interactive=True,extra_tests=[],coverage=True,reuse_db=False):
    # Set up logger
    if verbosity>1:
        get_logger().setLevel(logging.DEBUG)
    else:
        get_logger().setLevel(logging.INFO)
    # Mark testing environment
    settings.NOC_TEST=True
    suite=unittest.TestSuite()
    # Scan for tests
    print "Scanning for tests ...",
    modules,tsuite=get_tests(test_labels)
    test_cases=len(modules)+len(tsuite)
    print "... %d test module(s) found"%test_cases
    if not test_cases:
        print "... no tests found"
        return 1
    print "Preparing test cases ..."
    if coverage:
        # Initialize Coverage
        coverage=Coverage()
        coverage.exclude(r"^\s*$")                # Exclude empty lines
        coverage.exclude(r"^\s*#.*$")             # Exclude comment blocks
        coverage.exclude(r"^\s*(import|from)\s")  # Exclude import statements
        coverage.start()
    # Add docstrings and module load tests
    # Run inside Coverage context to cover loaded modules
    doctestOutputChecker = OutputChecker()
    for m in modules:
        # Module load
        suite.addTest(ImportTestCase(m))
        mt=["import"]
        # Docstrings
        try:
            suite.addTest(doctest.DocTestSuite(m,checker=doctestOutputChecker,runner=DocTestRunner))
            mt+=["doctest"]
        except ValueError,why:
            if "has no tests" not in why.args:
                raise Exception("Doctest error in %s: %s"%(m,why.args))
        if verbosity>1:
            print "adding tests for %s: %s"%(m,", ".join(mt))
    for m in tsuite:
        mo=__import__(m,{},{},"*")
        #suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(mo))
        tests=[]
        for name in dir(mo):
            obj=getattr(mo,name)
            if isinstance(obj, (type, types.ClassType)) and issubclass(obj, unittest.TestCase):
                if obj.__module__!="noc.lib.test":
                    tests.append(unittest.defaultTestLoader.loadTestsFromTestCase(obj))
        suite.addTest(unittest.TestSuite(tests))
    for test in extra_tests:
        suite.addTest(test)
    # Run tests
    print "Testing ..."
    setup_test_environment()
    settings.DEBUG = False
    from django.db import connection,connections
    old_names=[ connections[alias].settings_dict["NAME"] for alias in connections ]
    try:
        connection.cursor() # Raises operational error when no database exists
        has_db=True
    except:
        has_db=False
    # Create database when necessary
    if not reuse_db or not has_db:
        connection.creation.create_test_db(verbosity, autoclobber=not interactive)
        # Call sync-perm to install permissions
        management.call_command("sync-perm")
        management.call_command("sync-pyrules")
    # Run tests
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    # Drop database when necessary
    if not reuse_db:
        for name in old_names:
            connection.creation.destroy_test_db(name, verbosity)
    teardown_test_environment()

    test_results=len(result.failures) + len(result.errors)
    if coverage:
        coverage.stop()
        # Coverage HTML Report
        print "Writing Coverage report to %s"%settings.COVERAGE_REPORT_PATH
        coverage.html_report([mod_to_path(m) for m in modules]  , directory=settings.COVERAGE_REPORT_PATH)
        print "Done"
    return test_results
