# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Run noc tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand
from django.core import management
## Third-party modules
from south.management.commands import MigrateAndSyncCommand
## NOC modules
from noc.lib.test_runner import TestRunner


class Command(BaseCommand):
    """
    Customized version of django's test
    """
    option_list = BaseCommand.option_list + (
        make_option("--coverage", action="store_true", dest="coverage",
                    default=True, help="Generate Coverage report (default)"),
        make_option("--no-coverage", action="store_false", dest="coverage",
                    help="Skip Coverage report"),
        make_option("--reuse-db", action="store_true", dest="reuse_db",
                    default=False, help="Do not create testing DB when exists"),
    )
    help = 'Runs the test suite for the specified applications, or the entire project if no apps are specified.'
    args = '[appname ...]'

    requires_model_validation = False

    def handle(self, *test_labels, **options):
        from django.conf import settings

        verbosity = int(options.get("verbosity", 1))
        interactive = options.get("interactive", True)
        coverage = options.get("coverage", True)
        reuse_db = options.get("reuse_db", False)

        if (len(test_labels) == 1 and
            test_labels[0].startswith("noc.sa.profiles")):
            reuse_db = True
        # Install south migrations hook
        management.get_commands()
        management._commands["syncdb"] = MigrateAndSyncCommand()
        # Run tests
        failures = TestRunner(test_labels=test_labels, verbosity=verbosity,
                              interactive=interactive,
                              coverage=coverage, reuse_db=reuse_db).run()
        if failures:
            sys.exit(1 if failures else 0)
