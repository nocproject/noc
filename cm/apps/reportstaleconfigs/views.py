# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Stale Configs Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django.db.models import Q
## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.cm.models import Config
from noc.lib.dateutils import humanize_distance


class ReportStaleConfig(SimpleReport):
    title = "Stale Configs"

    STALE_INTERVAL = 2

    def get_data(self, **kwargs):
        d = (datetime.datetime.now() -
             datetime.timedelta(days=self.STALE_INTERVAL))
        q = Q(last_pull__isnull=True) | Q(last_pull__lt=d)
        return self.from_dataset(
            title=self.title,
            columns=[
                "Admin. Domain",
                "Object",
                "Profile",
                "Platform",
                "Address",
                "Last Pull"
            ],
            data=[(c.managed_object.administrative_domain.name,
                   c.managed_object.name,
                   c.managed_object.profile_name,
                   c.managed_object.platform,
                   c.managed_object.address,
                   humanize_distance(c.last_pull))
            for c in Config.objects.filter(q).order_by(
                "managed_object__administrative_domain__name")
            if c.is_stale],
            enumerate=True
        )
