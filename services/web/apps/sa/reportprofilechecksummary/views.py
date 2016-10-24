# -*- coding: utf-8 -*-
"""
##----------------------------------------------------------------------
## sa.reportprofilechecksummary
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""

from noc.lib.app.simplereport import SimpleReport, SectionRow, PredefinedReport
from noc.lib.nosql import get_db
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _


class ReportFilterApplication(SimpleReport):
    title = _("Managed Object Profile Check Summary")
    predefined_reports = {
        "default": PredefinedReport(
            _("Managed Object Profile Check Summary"), {}
        )
    }

    def get_data(self, request, **kwargs):
        data = []
        for p in Pool.objects.order_by("name"):
            data += [SectionRow(name=p.name)]

            is_managed = ManagedObject.objects.filter(is_managed=True, pool=p, profile_name="Generic.Host")
            is_managed_not_generic = ManagedObject.objects.filter(is_managed=True, pool=p).exclude(
                profile_name="Generic.Host")
            if not request.user.is_superuser:
                is_managed = is_managed.filter(administrative_domain__in=UserAccess.get_domains(request.user))
                is_managed_not_generic = is_managed_not_generic.filter(administrative_domain__in=
                                                                       UserAccess.get_domains(request.user))
                if not is_managed.count and not is_managed_not_generic.count:
                    data.pop()
                    continue

            is_alive = [s for s in is_managed if s.get_status()]

            is_managed_alive_in = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-" +
                                   str(m.id) for m in is_alive]
            is_managed_ng_in = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-" +
                                str(m.id) for m in is_managed_not_generic]

            bad_snmp_cred = get_db()["noc.joblog"].find({"problems.suggest_snmp": "Failed to guess SNMP community",
                                                         "_id": {"$in": is_managed_alive_in}}).count()
            bad_cli_cred = get_db()["noc.joblog"].find({"problems.suggest_cli": "Failed to guess CLI credentials",
                                                        "_id": {"$in": is_managed_ng_in}}).count()
            calc = [
                {"name": _("Not Managed"), "value": ManagedObject.objects.filter(is_managed=False, pool=p).count()},
                {"name": _("Is Managed"), "value": ManagedObject.objects.filter(is_managed=True, pool=p).count()},
                {"name": _("Is Managed, object type defined"), "value": is_managed_not_generic.count()},
                {"name": _("Is Managed, object type defined bad CLI Credential"), "value": bad_cli_cred},
                {"name": _("Is Managed, object type undefined"), "value": is_managed.count()},
                {"name": _("Is Managed, object type undefined not ping response"), "value":
                    len([s for s in is_managed if not s.get_status()])},
                {"name": _("Is Managed, object type undefined has ping response"), "value": len(is_alive)},
                {"name": _("Is Managed, object type undefined bad SNMP Credential"), "value": bad_snmp_cred},
                {"name": _("Is Managed, object type undefined for various reasons"), "value":
                    len(is_alive) - bad_snmp_cred},
            ]

            ALPHABET = {i[1]: i[0] for i in enumerate(u"npabcdefghijklmoqrstuvwxyz")}
            s1 = ["1.1", "1.2", "1.2.1", "1.2.1.1", "1.2.2", "1.2.2.1", "1.2.2.2", "1.2.2.2.1", "1.2.2.2.2"]
            for c in calc:
                data += [[s1[calc.index(c)], c["name"], c["value"]]]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("PP"),
                _("Status"),
                _("Quantity")
            ],
            data=data
        )
