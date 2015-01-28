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

