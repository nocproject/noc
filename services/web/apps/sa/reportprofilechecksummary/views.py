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
from noc.lib.nosql import get_db
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class ReportFilterApplication(SimpleReport):
    title = _("Managed Object Profile Check Summary")

    def get_data(self, **kwargs):
        data = []
        for p in Pool.objects.order_by("name"):
            data += [SectionRow(name=p.name)]

            is_managed = ManagedObject.objects.filter(is_managed=True, pool=p, profile_name="Generic.Host")
            is_managed_not_generic = ManagedObject.objects.filter(is_managed=True, pool=p).exclude(
                profile_name="Generic.Host")
            is_managed_in = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-" +
                             str(m.id) for m in is_managed]
            is_managed_ng_in = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-" +
                                str(m.id) for m in is_managed_not_generic]
            bad_snmp_cred = get_db()["noc.joblog"].find({"problems.suggest_snmp": "Failed to guess SNMP community",
                                                         "_id": {"$in": is_managed_in}}).count()
            bad_cli_cred = get_db()["noc.joblog"].find({"problems.suggest_cli": "Failed to guess CLI credentials",
                                                        "_id": {"$in": is_managed_ng_in}}).count()
            calc = {
                _("Not Managed"): ManagedObject.objects.filter(is_managed=False, pool=p).count(),
                _("Is Managed"): ManagedObject.objects.filter(is_managed=True, pool=p).count(),
                _("Not Generic.Host is Managed"): ManagedObject.objects.filter(pool=p, is_managed=True).exclude(
                    profile_name="Generic.Host").count(),
                _("Generic.Host is Managed"): is_managed.count(),
                _("Generic.Host is Managed ping"): len([s for s in is_managed if s.get_status()]),
                _("Generic.Host is Managed not ping"): len([s for s in is_managed if not s.get_status()]),
                _("Generic.Host is Managed bad SNMP Credential"): bad_snmp_cred,
                _("Is Managed bad CLI Credential"): bad_cli_cred,
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
