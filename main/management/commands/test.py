# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Run noc tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
import os
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
from django.core import management
## Third-party modules
from south.management.commands import MigrateAndSyncCommand
## NOC modules
from noc.lib.test_runner import TestRunner


class NoFlushCommand(BaseCommand):
    def handle(self, *args, **kwargs):
        pass


class Command(BaseCommand):
    """
    Customized version of django's test
    """
    option_list = BaseCommand.option_list + (
        make_option("--reuse-db", action="store_true", dest="reuse_db",
                    default=False, help="Do not create testing DB when exists"),
        make_option("--junit-xml-out", action="store", dest="junit_xml_out",
                    default=None, help="Write JUnit-compatible XML report"),
        make_option("--coverage-xml-out", action="store",
                    dest="coverage_xml_out", default=None,
                    help="Write Cobertura-compatible XML coverage report"),
        make_option("--coverage-html-out", action="store",
                    dest="coverage_html_out", default=None,
                    help="Write HTML coverage report"),
        make_option("--fixed-beef-base", action="store",
                    dest="fixed_beef_base", default=None,
                    help="Write fixed beefs into directory"),
        make_option("--interactive", action="store_true", dest="interactive",
                    default=True, help="Ask before dropping database"),
        make_option("--no-interactive", action="store_false",
                    dest="interactive",
                    default=True, help="Do not ask before dropping database")
    )
    help = 'Runs the test suite for the specified applications, or the entire project if no apps are specified.'
    args = '[appname ...]'

    requires_model_validation = False

    def handle(self, *test_labels, **options):
        verbosity = int(options.get("verbosity", 1))
        interactive = options.get("interactive", True)
        reuse_db = options.get("reuse_db", False)
        junit_xml_out = options.get("junit_xml_out")
        coverage_xml_out = options.get("coverage_xml_out")
        coverage_html_out = options.get("coverage_html_out")
        fixed_beef_base = options.get("fixed_beef_base")
        
        # Check directory for HTML coverage report exists
        if coverage_html_out:
            if not os.path.exists(coverage_html_out):
                os.makedirs(coverage_html_out)
            elif not os.path.isdir(coverage_html_out):
                raise CommandError("%d is not a directory" % coverage_html_out)
            elif not os.access(coverage_html_out, os.W_OK):
                raise CommandError("%d is not writable" % coverage_html_out)

        if (len(test_labels) == 1 and
            test_labels[0].startswith("noc.sa.profiles")):
            reuse_db = True
        # Install south migrations hook
        management.get_commands()
        management._commands["syncdb"] = MigrateAndSyncCommand()
        # Disable database flush
        management._commands["flush"] = NoFlushCommand()
        # Run tests
        failures = TestRunner(test_labels=test_labels, verbosity=verbosity,
                              interactive=interactive,
                              reuse_db=reuse_db,
                              junit_xml_out=junit_xml_out,
                              coverage_xml_out=coverage_xml_out,
                              coverage_html_out=coverage_html_out,
                              fixed_beef_base=fixed_beef_base).run()
        if failures:
            sys.exit(1 if failures else 0)
