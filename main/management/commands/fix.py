# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Collections management
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import sys
import uuid
# Django modules
from django.core.management.base import BaseCommand, CommandError
# NOC modules
from noc.core.debug import error_report
from noc.core.collection.base import Collection


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Fix database"

    def handle(self, *args, **kwargs):
        try:
            self.get_existing_mo()
            self.fix_uuids()
            self.fix_inv_root()
            self.fix_inv_lost_and_found()
            self.fix_inv_orphans()
            self.fix_fm_outage_orphans()
            self.fix_wiping_mo()
            self.fix_suspended_discovery_jobs()
            self.fix_db_interfaces_capability()
            self.fix_not_managed_alarms()
        except:
            error_report()
            sys.exit(1)

    def info(self, msg, *args):
        if args:
            print msg % args
        else:
            print msg

    def fix_uuids(self):
        """
        Fix collection uuids to binary format
        """
        self.info("Checking collections UUID")
        for c in Collection.iter_collections():
            c.fix_uuids()
        self.info("... done")

    def fix_inv_root(self):
        from noc.inv.models.object import Object
        from noc.inv.models.objectmodel import ObjectModel

        root_model = ObjectModel.objects.get(uuid="0f1b7c90-c611-4046-9a83-b120377eb6e0")
        self.info("Checking inventory Root")
        rc = Object.objects.filter(model=root_model.id).count()
        if rc == 0:
            # Create missed root
            self.info("    ... creating missed root")
            Object(model=root_model, name="Root").save()
        elif rc == 1:
            return  # OK
        else:
            # Merge roots
            roots = Object.objects.filter(model=root_model.id).order_by("id")
            r0 = roots[0]
            for r in roots[1:]:
                for o in Object.objects.filter(container=r.id):
                    self.info("    ... moving %s to primary root", unicode(o))
                    o.container = r0.id
                    o.save()
                self.info("   ... removing duplicated root %s", r)
                r.delete()

    def fix_inv_lost_and_found(self):
        from noc.inv.models.object import Object
        from noc.inv.models.objectmodel import ObjectModel

        lf_model = ObjectModel.objects.get(uuid="b0fae773-b214-4edf-be35-3468b53b03f2")
        self.info("Checking inventory Lost&Found")
        rc = Object.objects.filter(model=lf_model.id).count()
        if rc == 0:
            # Create missed l&f
            self.info("    ... creating missed Lost&Found")
            Object(model=lf_model, name="Global Lost&Found").save()
        elif rc == 1:
            return  # OK
        else:
            # Merge lost&founds
            lfs = Object.objects.filter(model=lf_model.id).order_by("id")
            r0 = lfs[0]
            for r in lfs[1:]:
                for o in Object.objects.filter(container=r.id):
                    self.info("    ... moving %s to primary Lost&Found", unicode(o))
                    o.container = r0.id
                    o.save()
                self.info("   ... removing duplicated lost&found %s", r.uuid)
                r.delete()

    def fix_inv_orphans(self):
        pass

    def fix_wiping_mo(self):
        from noc.sa.models.managedobject import ManagedObject
        from noc.sa.wipe.managedobject import wipe

        for mo in ManagedObject.objects.filter(name__startswith="wiping-"):
            wipe(mo)

    def fix_fm_outage_orphans(self):
        from fm.models.outage import Outage

        self.info("Checking fm.Outages")
        collection = Outage._get_collection()
        self.fix_missed_mo(collection, "object")

    def get_existing_mo(self):
        """
        Initialize set of existing managed objects ids
        :return:
        """
        from noc.sa.models.managedobject import ManagedObject

        self.existing_mo = set(
            ManagedObject.objects.exclude(
                name__startswith="wiping-"
            ).values_list("id", flat=True)
        )

    def get_missed_mo(self, collection, field):
        """
        Returns a list of missed objects in collection
        :param collection:
        :param fields:
        :return:
        """
        data = collection.aggregate([
            {
                "$group": {
                    "_id": "$%s" % field,
                    "count": {"$sum": 1}
                }
            }
        ])
        x = set(d["_id"] for d in data["result"])
        return list(x - self.existing_mo)

    def fix_missed_mo(self, collection, field):
        """
        Remove all records with missed objects
        :param collection:
        :param field:
        :return:
        """
        missed = self.get_missed_mo(collection, field)
        while missed:
            chunk, missed = missed[:500], missed[500:]
            self.info(
                "    ... Removing records for %s",
                ", ".join(str(x) for x in chunk)
            )
            collection.remove({
                field: {
                    "$in": chunk
                }
            })

    def fix_suspended_discovery_jobs(self):
        """
        Suspend/resumed discovery jobs
        """
        from noc.sa.models.managedobject import ManagedObject

        self.info("Suspending/Resuming discovery jobs")
        for o in ManagedObject.objects.filter(is_managed=True):
            o.ensure_discovery_jobs()

    def fix_db_interfaces_capability(self):
        """
        Fixing DB | Interfaces capability
        """
        from noc.inv.models.interface import Interface
        from noc.sa.models.managedobject import ManagedObject

        self.info("Fixing *DB | Interfaces* capability")
        r = Interface._get_collection().aggregate([{
            "$group": {
                "_id": "$managed_object",
                "count": {
                    "$sum": 1
                }
            }
        }])
        if not "ok" in r:
            self.info("    ... error")
            return
        # Process capabilities
        caps = dict((x["_id"], x["count"]) for x in r["result"])
        for o in ManagedObject.objects.filter(is_managed=True):
            if o.id in caps:
                o.update_caps({
                    "DB | Interfaces": caps[o.id]
                }, source="interface")

    def fix_not_managed_alarms(self):
        """
        Close all active alarms belonging to non-managed objects
        """
        from noc.sa.models.managedobject import ManagedObject
        from noc.fm.models.activealarm import ActiveAlarm
        self.info("Fixing hanging alarms")
        nmo = ManagedObject.objects.filter(
            is_managed=False
        ).values_list("id", flat=True)
        for a in ActiveAlarm.objects.filter(
            managed_object__in=nmo
        ):
            self.info("   Closing alarm %s (%s)",
                      a.id, a.managed_object.name)
            a.clear_alarm("Closed by fix (management is disabled)")
