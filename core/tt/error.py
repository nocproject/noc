# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# TTSystem errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class TTError(Exception):
    pass


class TemporaryTTError(TTError):
    """
    TTSystem can raise TemporaryTTError for calls that can be restarted
    later
    """
    pass
