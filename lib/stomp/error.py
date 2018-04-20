# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## STOMP Protocol errors
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

class STOMPError(Exception):
    """STOMP Protocol Error"""


class STOMPNotConnected(Exception):
    """Client is not connected"""
