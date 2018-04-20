# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test Environment Context
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.conf import settings
from django.test.utils import setup_test_environment, teardown_test_environment


class TestEnvironmentContext(object):
    """
    Test environment context manager
    """
    def __enter__(self):
        # Save old settings
        self.old_is_test = settings.IS_TEST
        self.old_debug = settings.DEBUG
        # Temporary change settings
        settings.IS_TEST = True
        settings.DEBUG = False
        # Setup environment
        setup_test_environment()

    def __exit__(self, exc_type, exc_value, traceback):
        # Destroy test environment
        teardown_test_environment()
        # Restore settings
        settings.IS_TEST = self.old_is_test
        settings.DEBUG = self.old_debug
