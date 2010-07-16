# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Run noc tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.core.management.base import BaseCommand
from django.core import management
from south.management.commands import MigrateAndSyncCommand
from optparse import make_option
import sys
##
## Customized version of Django's test
##
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--coverage",action="store_true",dest="coverage",default=True,
            help="Generate Coverage report (default)"),
        make_option("--no-coverage",action="store_false",dest="coverage",
            help="Skip Coverage report"),
        make_option("--reuse-db",action="store_true",dest="reuse_db",default=False,
            help="Do not create testing DB when exists"),
    )
    help = 'Runs the test suite for the specified applications, or the entire project if no apps are specified.'
    args = '[appname ...]'

    requires_model_validation = False

    def handle(self, *test_labels, **options):
        from django.conf import settings
        from django.test.utils import get_runner
        verbosity=int(options.get("verbosity", 1))
        interactive=options.get("interactive", True)
        coverage=options.get("coverage",True)
        reuse_db=options.get("reuse_db",False)
        test_runner = get_runner(settings)
        
        # Install south migrations hook
        management.get_commands()
        management._commands['syncdb'] = MigrateAndSyncCommand()
        # Run tests
        failures = test_runner(test_labels, verbosity=verbosity, interactive=interactive,coverage=coverage,reuse_db=reuse_db)
        if failures:
            sys.exit(bool(failures))
