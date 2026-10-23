# ---------------------------------------------------------------------
# Script context managers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


class ConfigurationContextManager:
    """Configuration context manager to use with "with" statement"""

    def __init__(self, script) -> None:
        self.script = script

    def __enter__(self):
        """Entering configuration context"""
        self.script.enter_config()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Leaving configuration context"""
        if exc_type is None:
            self.script.leave_config()


class CacheContextManager:
    def __init__(self, script) -> None:
        self.script = script
        self.changed = False

    def __enter__(self):
        if not self.script.root.is_cached:
            self.changed = True
            self.script.root.is_cached = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.changed:
            self.script.root.is_cached = False


class IgnoredExceptionsContextManager:
    """Silently ignore specific exceptions"""

    def __init__(self, iterable) -> None:
        self.exceptions = set(iterable)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and exc_type in self.exceptions:
            return True  # Suppress exception
