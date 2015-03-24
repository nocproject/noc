# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Collections management
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
import uuid
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.debug import error_report
from noc.main.management.commands.collection import Command as CollectionCommand


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Fix database"

    def handle(self, *args, **kwargs):
        try:
            self.fix_uuids()
            self.fix_inv_root()
            self.fix_inv_lost_and_found()
            self.fix_inv_orphans()
            self.fix_metricsettings()
            self.fix_wiping_mo()
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
        for n, c in CollectionCommand.collections:
            if ("uuid" in c._fields and
                    hasattr(c._fields["uuid"], "_binary") and
                    c._fields["uuid"]._binary
                ):
                self.fix_collection_uuids(n, c)
        self.info("... done")

    def fix_collection_uuids(self, name, collection):
        c = collection._get_collection()
        for doc in c.find({
            "uuid": {
                "$type": 2  # string type
            }
        }, {"uuid": 1}):
            self.info("    Fix %s UUID %s", name, doc["uuid"])
            c.update(
                {"_id": doc["_id"]},
                {
                    "$set": {
                        "uuid": uuid.UUID(doc["uuid"])
                    }
                }
            )


    def fix_metricsettings(self):
        def remove_ms(ms):
            MetricSettings._get_collection().remove({"_id": ms.id})

        from noc.pm.models.metricsettings import MetricSettings
        self.info("Checking pm.MetricSettings")
        for ms in MetricSettings.objects.all():
            # Check referenced object is exists
            if not ms.get_object():
                self.info(
                    "    ... Unable to dereference %s:%s. Removing",
                    ms.model_id, ms.object_id
                )
                remove_ms(ms)
                continue
            # Check metric sets references
            msl = []
            for m in ms.metric_sets:
                try:
                    x = m.metric_set
                    msl += [m]
                except Exception, why:
                    self.info("    ... Unable to dereference metric set. Pulling")
            if len(msl) < len(ms.metric_sets):
                ms.metric_sets = msl
                ms.save()
            # Remove empty metric sets
            if not ms.metric_sets:
                self.info(
                    "    ... Empty metric sets for %s:%s. Removing",
                    ms.model_id, ms.object_id
                )
                remove_ms(ms)
                continue
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
        from noc.lib.nosql import get_db
        from noc.lib.scheduler.utils import submit_job

        c = get_db().noc.schedules.main.jobs
        for mo in ManagedObject.objects.filter(name__startswith="wiping-"):
            if not c.find({"object": mo.id, "jcls": "sa.wipe_managed_object"}).count():
                self.info("Restarting wipe process: %s", mo)
                submit_job("main.jobs", "sa.wipe_managed_object", mo.id)
