# ---------------------------------------------------------------------
# Discovery handlers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.inv.models.interface import Interface


def _get_interface(object, name):
    Interface._get_collection().update_many({"managed_object": object.id})


def oper_up(event):
    """
    Set oper status to up
    """
    iface = Interface.objects.filter(
        managed_object=event.managed_object.id, name=event.vars["interface"]
    ).first()
    if iface:
        iface.set_oper_status(True)
        event.set_hint("link_status", True)


def oper_down(event):
    """
    Set oper status to down
    """
    iface = Interface.objects.filter(
        managed_object=event.managed_object.id, name=event.vars["interface"]
    ).first()
    if iface:
        iface.set_oper_status(False)
        event.set_hint("link_status", False)
