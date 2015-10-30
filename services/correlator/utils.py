# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Helper functions seen as utils.* in conditional rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2012, The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link

logger = logging.getLogger(__name__)


def linked_object(object, interface):
    """
    Returns managed object linked to object:interface or None
    """
    try:
        cn = object.profile.convert_interface_name(interface)
    except Exception, why:
        logger.error("Cannot convert interface name '%s': %s",
                     interface, why)
        return None
    iface = Interface.objects.filter(managed_object=object.id, name=cn).first()
    if not iface:
        logger.debug("Interface %s@%s is not found",
                     object.name, cn)
        return None
    link = Link.objects.filter(interfaces=iface.id).first()
    if not link:
        logger.debug("Link not found for %s@%s", object.name, cn)
        return None
    mo = set()
    for i in link.interfaces:
        if i.managed_object.id != object.id:
            mo.add(i.managed_object)
    if len(mo) == 1:
        return mo.pop()
    else:
        logger.debug("No linked managed objects found")
        return None
