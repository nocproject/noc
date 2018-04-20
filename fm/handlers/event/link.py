# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Discovery handlers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.inv.models.interface import Interface


def _get_interface(object, name):
    Interface._get_collection().update({
        "managed_object": object.id
    })
=======
##----------------------------------------------------------------------
## Discovery handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.inv.models.interfacestatus import InterfaceStatus
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


def oper_up(event):
    """
    Set oper status to up
    """
<<<<<<< HEAD
    iface = Interface.objects.filter(
        managed_object=event.managed_object.id,
        name=event.vars["interface"]
    ).first()
    if iface:
        iface.set_oper_status(True)
=======
    i_name = event.vars["interface"]
    InterfaceStatus.set_status(
        event.managed_object, i_name, oper_status=True)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


def oper_down(event):
    """
    Set oper status to down
    """
<<<<<<< HEAD
    iface = Interface.objects.filter(
        managed_object=event.managed_object.id,
        name=event.vars["interface"]
    ).first()
    if iface:
        iface.set_oper_status(False)
=======
    i_name = event.vars["interface"]
    InterfaceStatus.set_status(
        event.managed_object, i_name, oper_status=False)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
