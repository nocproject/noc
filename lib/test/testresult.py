# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test Result formatter
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
import time
import logging
## Django modules
from django.utils import unittest  # unittest2 backport
## NOC modules
from teestream import TeeStream
from noc.lib.debug import format_frames, get_traceback_frames
from noc.lib.fileutils import safe_rewrite


class NOCTestResult(unittest.TestResult):
    """
    Test result with JUnit-compatible XML generator
    """
    R_SUCCESS = 0
    R_ERROR = 1
    R_FAILURE = 2

    def __init__(self, *args, **kwargs):
        super(NOCTestResult, self).__init__(*args, **kwargs)
        self.test_results = []  # (name, test, R_*, err | None)
        self.test_timings = {}
        self.stdout = TeeStream(sys.stdout)
        self.stderr = TeeStream(sys.stderr)

    def startTestRun(self):
        """
        Called once before any tests are executed.
        """
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        self.start_time = time.time()

    def stopTestRun(self):
        """
        Called once after all tests are executed.
        """
        self.stop_time = time.time()
        sys.stdout = self.stdout.orig
        sys.stderr = self.stderr.orig

    def addSuccess(self, test):
        self.test_results += [(test.id(), test, self.R_SUCCESS, None)]
        super(NOCTestResult, self).addSuccess(test)

    def addError(self, test, err):
        self.test_results += [(test.id(), test, self.R_ERROR, err)]
        super(NOCTestResult, self).addError(test, err)

    def addFailure(self, test, err):
        self.test_results += [(test.id(), test, self.R_FAILURE, err)]
        super(NOCTestResult, self).addFailure(test, err)

    def startTest(self, test):
        self.testsRun += 1
        self.test_timings[test.id()] = time.time()

    def stopTest(self, test):
        t = test.id()
        self.test_timings[t] = time.time() - self.test_timings[t]

    def dump_result(self):
        if len(self.errors) + len(self.failures):
            print "Failed tests:"
            print
        for name, test, status, err in sorted(self.test_results,
                                              key=lambda x: x[0]):
            if status in (self.R_ERROR, self.R_FAILURE):
                print ">>> %s: %s" % (name, test.shortDescription())
                print "%s: %s" % (err[0].__name__, err[1])
                print format_frames(get_traceback_frames(err[2]))
                print

    def write_xml(self, path):
        """
        Generator returning JUnit-compatible XML output
        """
        from xml.dom.minidom import Document

        logging.info("Writing JUnit XML output to '%s'" % path)
        out = Document()
        ts = out.createElement("testsuite")
        out.appendChild(ts)
        ts.setAttribute("tests", str(self.testsRun))
        ts.setAttribute("errors", str(len(self.errors)))
        ts.setAttribute("failures", str(len(self.failures)))
        #ts.setAttribute("name")
        ts.setAttribute("time", str(self.stop_time - self.start_time))
        ts.setAttribute("timestamp", self.timestamp)
        # Append test cases info
        for name, test, status, err in sorted(self.test_results,
                                              key=lambda x: x[0]):
            p = name.split(".")
            tc = out.createElement("testcase")
            ts.appendChild(tc)
            tc.setAttribute("classname", ".".join(p[:-1]))
            tc.setAttribute("name", p[-1])
            tc.setAttribute("time", "%.6f" % self.test_timings[name])
            if status in (self.R_ERROR, self.R_FAILURE):
                e = out.createElement("error" if self.R_ERROR else "failure")
                tc.appendChild(e)
                e.setAttribute("type", err[0].__name__)
                e.setAttribute("message", str(err[1]))
                ft = out.createCDATASection(
                    "%s: %s" % (err[0].__name__, err[1]) + "\n" +
                    format_frames(get_traceback_frames(err[2])) + "\n")
                e.appendChild(ft)
        # Applend system-out and system-err
        so = out.createElement("system-out")
        o = out.createCDATASection(self.stdout.get())
        so.appendChild(o)
        ts.appendChild(so)
        se = out.createElement("system-err")
        o = out.createCDATASection(self.stderr.get())
        se.appendChild(o)
        ts.appendChild(se)
        r = out.toprettyxml(indent=" " * 4)
        if path == "-":
            print r
        else:
            safe_rewrite(path, r)
