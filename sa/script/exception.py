# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Exception classes
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class TimeOutError(Exception):
    """Operation timed out"""


class LoginError(Exception):
    """Login Failed"""


class CLISyntaxError(Exception):
    """CLI reports syntax error"""


class CLIOperationError(Exception):
    """CLI Operation returns error (Except of Syntax Error)"""


class NotSupportedError(Exception):
    """Feature is not supported on current platform/software/feature set"""


class UnexpectedResultError(Exception):
    """Command returns result that cannot be parsed"""


class CancelledError(Exception):
    """Script cancelled"""


class UnexpectedPagerPattern(Exception):
    """Invalid pager pattern set"""


class UnknownAccessScheme(Exception):
    """Unknown access schema"""


class InvalidPagerPattern(Exception):
    """Invalid pager pattern"""
