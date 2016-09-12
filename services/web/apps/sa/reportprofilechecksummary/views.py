# -*- coding: utf-8 -*-
"""
##----------------------------------------------------------------------
## sa.reportprofilechecksummary
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""

from noc.lib.app.simplereport import SimpleReport, SectionRow
from noc.main.models.pool import Pool
from noc.core.translation import ugettext as _
from noc.sa.models.managedobject import ManagedObject


class ReportFilterApplication(SimpleReport):
    title = _("ManagedObject Profile Check Summary")

    def get_data(self, **kwargs):
        data = []
        # pools = Pool.objects.filter()
        for p in Pool.objects.order_by("name"):
            data += [SectionRow(name=p.name)]
            is_managed = ManagedObject.objects.filter(is_managed=True, pool=p, profile_name="Generic.Host")
            calc = {
                _("Not Managed"): ManagedObject.objects.filter(is_managed=False, pool=p).count(),
                _("Is Managed"): ManagedObject.objects.filter(is_managed=True, pool=p).count(),
                _("Not Generic.Host is Managed"): ManagedObject.objects.filter(pool=p, is_managed=True).exclude(
                    profile_name="Generic.Host").count(),
                _("Generic.Host is Managed"): is_managed.count(),
                _("Generic.Host is Managed ping"): len([s for s in is_managed if s.get_status()]),
                _("Generic.Host is Managed not ping"): len([s for s in is_managed if not s.get_status()]),
            }

            for c in calc:
                data += [[c, calc[c]]]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Status"),
                _("Quantity")
            ],
            data=data
        )
