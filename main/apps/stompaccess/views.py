# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.stompaccess application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.main.models import StompAccess


class StompAccessApplication(ExtDocApplication):
    """
    StompAccess application
    """
    title = "STOMP Access"
    menu = "Setup | STOMP Access"
    model = StompAccess
