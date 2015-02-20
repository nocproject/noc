# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Wipe managed object
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from noc.lib.log import PrefixLoggerAdapter
from noc.sa.models.managedobject import ManagedObjectAttribute
from noc.sa.models.maptask import MapTask
from noc.inv.models.forwardinginstance import ForwardingInstance
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.link import Link
from noc.inv.models.macdb import MACDB
from noc.inv.models.pendinglinkcheck import PendingLinkCheck
from noc.inv.models.discoveryid import DiscoveryID
from noc.sa.models.objectcapabilities import ObjectCapabilities
from noc.fm.models.newevent import NewEvent
from noc.fm.models.failedevent import FailedEvent
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.archivedevent import ArchivedEvent
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.outage import Outage
from noc.sa.models.objectstatus import ObjectStatus
from noc.ip.models import Address
from noc.lib.nosql import get_db

logger = logging.getLogger(__name__)


def wipe(o):
    if o.profile_name.startswith("NOC."):
        return True
    log = PrefixLoggerAdapter(logger, str(o.id))
    # Delete active map tasks
    log.debug("Wiping MAP tasks")
    MapTask.objects.filter(managed_object=o).delete()
    # Wiping discovery tasks
    log.debug("Wiping discovery tasks")
    db = get_db()
    db.noc.schedules.inv.discovery.remove({"key": o.id})
    # Wiping FM events
    log.debug("Wiping events")
    NewEvent.objects.filter(managed_object=o.id).delete()
    FailedEvent.objects.filter(managed_object=o.id).delete()
    ActiveEvent.objects.filter(managed_object=o.id).delete()
    ArchivedEvent.objects.filter(managed_object=o.id).delete()
    # Wiping alarms
    log.debug("Wiping alarms")
    for ac in (ActiveAlarm, ArchivedAlarm):
        for a in ac.objects.filter(managed_object=o.id):
            # Relink root causes
            my_root = a.root
            for iac in (ActiveAlarm, ArchivedAlarm):
                for ia in iac.objects.filter(root=a.id):
                    ia.root = my_root
                    ia.save()
            # Delete alarm
            a.delete()
    # Wiping MAC DB
    log.debug("Wiping MAC DB")
    MACDB._get_collection().remove({"managed_object": o.id})
    # Wiping pending link check
    log.debug("Wiping pending link check")
    PendingLinkCheck._get_collection().remove({"local_object": o.id})
    PendingLinkCheck._get_collection().remove({"remote_object": o.id})
    # Wiping discovery id cache
    log.debug("Wiping discovery id")
    DiscoveryID._get_collection().remove({"object": o.id})
    # Wiping interfaces, subs and links
    # Wipe links
    log.debug("Wiping links")
    for i in Interface.objects.filter(managed_object=o.id):
        # @todo: Remove aggregated links correctly
        Link.objects.filter(interfaces=i.id).delete()
    #
    log.debug("Wiping subinterfaces")
    SubInterface.objects.filter(managed_object=o.id).delete()
    log.debug("Wiping interfaces")
    Interface.objects.filter(managed_object=o.id).delete()
    log.debug("Wiping forwarding instances")
    ForwardingInstance.objects.filter(managed_object=o.id).delete()
    # Unbind from IPAM
    log.debug("Unbind from IPAM")
    for a in Address.objects.filter(managed_object=o):
        a.managed_object = None
        a.save()
    # Wipe object status
    log.debug("Wiping object status")
    ObjectStatus.objects.filter(object=o.id).delete()
    # Wipe outages
    log.debug("Wiping outages")
    Outage.objects.filter(object=o.id).delete()
    # Delete Managed Object's capabilities
    log.debug("Wiping capabilitites")
    ObjectCapabilities.objects.filter(object=o.id).delete()
    # Delete Managed Object's attributes
    log.debug("Wiping attributes")
    ManagedObjectAttribute.objects.filter(managed_object=o).delete()
    # Finally delete object and config
    log.debug("Finally wiping object")
    o.delete()
    log.debug("Done")

