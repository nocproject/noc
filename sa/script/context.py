# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Script context managers
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class ConfigurationContextManager(object):
    """Configuration context manager to use with "with" statement"""
    def __init__(self, script):
        self.script = script

    def __enter__(self):
        """Entering configuration context"""
        self.script.enter_config()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Leaving configuration context"""
        if exc_type is None:
            self.script.leave_config()


class CancellableContextManager(object):
    """Mark cancelable part of script"""
    def __init__(self, script):
        self.script = script

    def __enter__(self):
        self.script.is_cancelable = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.is_cancelable = False


class IgnoredExceptionsContextManager(object):
    """Silently ignore specific exceptions"""
    def __init__(self, iterable):
        self.exceptions = set(iterable)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and exc_type in self.exceptions:
            return True  # Suppress exception


class CacheContextManager(object):
    def __init__(self, script):
        self.script = script
        self.changed = False

    def __enter__(self):
        if not self.script.root.is_cached:
            self.changed = True
            self.script.root.is_cached = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.changed:
            self.script.root.is_cached = False
