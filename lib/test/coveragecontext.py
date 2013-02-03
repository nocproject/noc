# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Coverage Context
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Third-party modules
from coverage import coverage as Coverage


class CoverageContext(object):
    """
    Coverage context manager
    """
    def __init__(self, runner, xml_out=None, html_out=None):
        self.runner = runner
        self.enable = xml_out is not None or html_out is not None
        self.xml_out = xml_out
        self.html_out = html_out
        if self.enable:
            self.coverage = Coverage(config_file=False,
                                     source=self.runner.coverage_report)
            self.coverage.exclude(r"^\s*$")  # Exclude empty lines
            self.coverage.exclude(r"^\s*#.*$")  # Exclude comment blocks
            self.coverage.exclude(r"^\s*(import|from)\s")  # Exclude import statements
        else:
            self.coverage = None

    def info(self, message):
        logging.info(message)

    def __enter__(self):
        if self.coverage:
            self.info("Starting coverage")
            self.coverage.start()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.coverage:
            self.info("Stopping coverage")
            self.coverage.stop()
            if self.xml_out:
                self.info("Writing Cobertura-compatible XML coverage report "
                          " to %s" % self.xml_out)
                self.coverage.xml_report(outfile=self.xml_out)
            if self.html_out:
                self.info("Writing HTML coverage report to %s" % self.html_out)
                self.coverage.html_report(directory=self.html_out)
