# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc sync
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import csv
import sys
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.main.models.synccache import SyncCache


class Command(BaseCommand):
    def handle(self, *args, **options):
        writer = csv.writer(sys.stdout)
        h = ["UUID", "Model", "Object ID", "Object", "Sync",
             "instance", "Changed", "Expire"]
        writer.writerow(h)
        for sc in SyncCache.objects.all():
            writer.writerow([
                sc.uuid, sc.model_id, sc.object_id, unicode(sc.get_object()),
                sc.sync_id, sc.instance_id, sc.changed.isoformat(),
                sc.expire.isoformat()
            ])
