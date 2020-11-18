# ----------------------------------------------------------------------
# TTSystem errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class TTError(Exception):
    """
    Base class for TT Errors
    """


class TemporaryTTError(TTError):
    """
    TTSystem can raise TemporaryTTError for calls that can be restarted
    later
    """
