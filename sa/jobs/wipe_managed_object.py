# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Wipe managed object
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models import ManagedObjectAttribute
from noc.sa.models.maptask import MapTask
from noc.inv.models import (ForwardingInstance,
                           Interface, SubInterface, Link,
                           MACDB)
from noc.inv.models.pendinglinkcheck import PendingLinkCheck
from noc.inv.models.discoveryid import DiscoveryID
from noc.fm.models import (
    NewEvent, FailedEvent, ActiveEvent, ArchivedEvent,
    ActiveAlarm, ArchivedAlarm)
from noc.ip.models import Address
from noc.lib.scheduler.job import Job


class WipeManagedObject(Job):
    name = "sa.wipe_managed_object"
    model = ManagedObject

    def handler(self, *args, **kwargs):
        o = self.object
        if o.profile_name.startswith("NOC."):
            return True
        # Wiping FM events
        NewEvent.objects.filter(managed_object=o.id).delete()
        FailedEvent.objects.filter(managed_object=o.id).delete()
        ActiveEvent.objects.filter(managed_object=o.id).delete()
        ArchivedEvent.objects.filter(managed_object=o.id).delete()
        # Wiping alarms
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
        MACDB._get_collection().remove({"managed_object": o.id})
        # Wiping pending link check
        PendingLinkCheck._get_collection().remove({"local_object": o.id})
        PendingLinkCheck._get_collection().remove({"remote_object": o.id})
        # Wiping discovery id cache
        DiscoveryID._get_collection().remove({"object": o.id})
        # Wiping interfaces, subs and links
        # Wipe links
        for i in Interface.objects.filter(managed_object=o.id):
            # @todo: Remove aggregated links correctly
            Link.objects.filter(interfaces=i.id).delete()
        #
        ForwardingInstance.objects.filter(managed_object=o.id).delete()
        Interface.objects.filter(managed_object=o.id).delete()
        SubInterface.objects.filter(managed_object=o.id).delete()
        # Unbind from IPAM
        for a in Address.objects.filter(managed_object=o):
            a.managed_object = None
            a.save()
        # Delete active map tasks
        MapTask.objects.filter(managed_object=o).delete()
        # Delete Managed Object's attributes
        ManagedObjectAttribute.objects.filter(managed_object=o).delete()
        # Finally delete object and config
        o.delete()
        return True
