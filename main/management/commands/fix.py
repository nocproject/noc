# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Collections management
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import make_option
import os
import stat
import sys
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.collection import Collection, DereferenceError
from noc.main.models.doccategory import DocCategory
from noc.gis.models.layer import Layer
from noc.inv.models.technology import Technology
from noc.inv.models.vendor import Vendor
from noc.inv.models.modelinterface import ModelInterface
from noc.inv.models.connectiontype import ConnectionType
from noc.inv.models.connectionrule import ConnectionRule
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.capability import Capability
from noc.fm.models.oidalias import OIDAlias
from noc.fm.models.syntaxalias import SyntaxAlias
from noc.fm.models.mibalias import MIBAlias
from noc.fm.models.mibpreference import MIBPreference
from noc.fm.models.enumeration import Enumeration
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.eventclass import EventClass
from noc.fm.models.eventclassificationrule import EventClassificationRule
from noc.fm.models.cloneclassificationrule import CloneClassificationRule
from noc.pm.models.metrictype import MetricType
from noc.lib.serialize import json_decode
from noc.lib.fileutils import read_file
from noc.lib.debug import error_report


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Fix database"

    def handle(self, *args, **kwargs):
        self.fix_inv_root()
        self.fix_inv_lost_and_found()
        self.fix_inv_orphans()
        self.fix_metricsettings()

    def info(self, msg, *args):
        if args:
            print msg % args
        else:
            print msg

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
