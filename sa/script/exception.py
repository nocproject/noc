# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Exception classes
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Operation timed out
class TimeOutError(Exception): pass
## Login Failed
class LoginError(Exception): pass
## CLI reports syntax error
class CLISyntaxError(Exception): pass
## Feature is not supported on current platform/software/feature set
class NotSupportedError(Exception): pass
## Commands returns result that cannot be parsed
class UnexpectedResultError(Exception): pass
## Script cancelled
class CancelledError(Exception): pass
## Invalid pager pattern occured
class UnexpectedPagerPattern(Exception): pass
## Unknown access schema
class UnknownAccessScheme(Exception): pass