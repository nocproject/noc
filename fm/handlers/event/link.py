# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.inv.models.interface import Interface


def _get_interface(object, name):
    Interface._get_collection().update({
        "managed_object": object.id
    })


def oper_up(event):
    """
    Set oper status to up
    """
    iface = Interface.objects.filter(
        managed_object=event.managed_object.id,
        name=event.vars["interface"]
    ).first()
    if iface:
        iface.set_oper_status(True)


def oper_down(event):
    """
    Set oper status to down
    """
    iface = Interface.objects.filter(
        managed_object=event.managed_object.id,
        name=event.vars["interface"]
    ).first()
    if iface:
        iface.set_oper_status(False)
