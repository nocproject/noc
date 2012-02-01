# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc wipe
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import sys
from contextlib import contextmanager
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.validators import is_int


class Command(BaseCommand):
    args = "<model> <object id> [.. <object id>]"
    help = "Completely wipe object and related data"

    models = ["managed_object"]

    def handle(self, *args, **options):
        if len(args) < 1:
            print "USAGE: %s <model> <object id> [.. <object id>]" % sys.argv[0]
            sys.exit(1)
        m = args[0].replace("-", "_")
        if m not in self.models:
            raise CommandError("Invalid model '%s'. Valid models are: %s" % (
                m, ", ".join(self.models)))
        objects = []
        getter = getattr(self, "get_%s" % m)
        wiper = getattr(self, "wipe_%s" % m)
        # Get objects
        for o_id in args[1:]:
            o = getter(o_id)
            if not o:  # Not found
                raise CommandError("Object '%s' is not found" % o_id)
            objects += [o]
        # Wipe objects
        for o in objects:
            with self.log("Wiping '%s':" % unicode(o), True):
                wiper(o)

    @contextmanager
    def log(self, message, newline=False):
        """
        Progress log wrapper. Usage:
        with self.log(message):
            do something

        :param message:
        :param newline: Add newline
        :return:
        """
        if newline:
            message += "\n"
        else:
            message = "    " + message + " ... "
        sys.stdout.write(message)
        sys.stdout.flush()
        yield
        sys.stdout.write("done\n")
        sys.stdout.flush()

    def get_managed_object(self, o_id):
        """
        Get ManagedObject by id or name
        :param o_id: Object's id or name
        :return: ManagedObject
        :rtype: ManagedObject
        """
        from noc.sa.models import ManagedObject

        # Try to get object by id
        if is_int(o_id):
            try:
                return ManagedObject.objects.get(id=int(o_id))
            except ManagedObject.DoesNotExist:
                pass
        # Try to get object by name
        try:
            return ManagedObject.objects.get(name=o_id)
        except ManagedObject.DoesNotExist:
            return None

    def wipe_managed_object(self, o):
        """
        Wipe Managed Object
        :param o: Managed Object
        :type o: Managed Object
        :return: None
        """
        from noc.sa.models import ManagedObjectAttribute
        from noc.inv.models import Interface, SubInterface, Link,\
                                   DiscoveryStatusInterface
        from noc.fm.models import NewEvent, FailedEvent,\
                                  ActiveEvent, ArchivedEvent,\
                                  ActiveAlarm, ArchivedAlarm
        from noc.ip.models import Address

        if o.profile_name.startswith("NOC."):
            raise CommandError("Cannot wipe internal object '%s'" % unicode(o))
        # Wiping FM events
        with self.log("Deleting new events"):
            NewEvent.objects.filter(managed_object=o.id).delete()
        with self.log("Deleting failed events"):
            FailedEvent.objects.filter(managed_object=o.id).delete()
        with self.log("Deleting active events"):
            ActiveEvent.objects.filter(managed_object=o.id).delete()
        with self.log("Deleting archived events"):
            ArchivedEvent.objects.filter(managed_object=o.id).delete()
        # Wiping alarms
        with self.log("Deleting alarms"):
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
        # Wiping interfaces, subs and links
        with self.log("Deleting interfaces, subinterfaces and links"):
            for i in Interface.objects.filter(managed_object=o.id):
                # Wipe subinterfaces
                SubInterface.objects.filter(interface=i.id).delete()
                # Wipe links
                # @todo: Remove aggregated links correctly
                Link.objects.filter(interfaces=i.id).delete()
                # Wipe interface
                i.delete()
        # Delete interface discovery status
        with self.log("Cleaning interface discovery status"):
            DiscoveryStatusInterface.objects.filter(managed_object=o.id).delete()
        # Unbind from IPAM
        with self.log("Unbinding from IPAM"):
            for a in Address.objects.filter(managed_object=o):
                a.managed_object = None
                a.save()
        # Delete Managed Object's attributes
        with self.log("Deleting object's attributes"):
            ManagedObjectAttribute.objects.filter(managed_object=o).delete()
        # Finally delete object and config
        with self.log("Deleting managed object and config"):
            o.delete()
