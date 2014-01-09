# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.inv.models.interfacestatus import InterfaceStatus


def oper_up(event):
    """
    Set oper status to up
    """
    i_name = event.vars["interface"]
    InterfaceStatus.set_status(
        event.managed_object, i_name, oper_status=True)


def oper_down(event):
    """
    Set oper status to down
    """
    i_name = event.vars["interface"]
    InterfaceStatus.set_status(
        event.managed_object, i_name, oper_status=False)
