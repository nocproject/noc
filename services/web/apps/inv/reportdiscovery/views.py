# ---------------------------------------------------------------------
# inv.reportdiscovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.simplereport import SimpleReport, SectionRow, TableColumn
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.link import Link
from noc.core.translation import ugettext as _


class ReportDiscoveryApplication(SimpleReport):
    title = _("Discovery Summary")

    def get_data(self, **kwargs):
        data = []
        # Managed objects summary
        data += [SectionRow("Managed Objects")]
        d = []
        j_box = 0
        j_box_sec = 0.0
        j_periodic = 0
        j_periodic_sec = 0.0
        for p in ManagedObjectProfile.objects.all():
            o_count = ManagedObject.objects.filter(is_managed=True, object_profile=p).count()
            d += [[p.name, o_count]]
            if p.enable_box_discovery:
                j_box += o_count
                j_box_sec += float(o_count) / p.box_discovery_interval
            if p.enable_periodic_discovery:
                j_periodic += o_count
                j_periodic_sec += float(o_count) / p.periodic_discovery_interval
        data += sorted(d, key=lambda x: -x[1])
        # Interface summary
        d = []
        data += [SectionRow("Interfaces")]
        d_count = Interface.objects.count()
        for p in InterfaceProfile.objects.all():
            n = Interface.objects.filter(profile=p).count()
            d += [[p.name, n]]
            d_count -= n
        data += sorted(d, key=lambda x: -x[1])
        data += [["-", d_count]]
        # Links summary
        data += [SectionRow("Links")]
        r = Link._get_collection().aggregate(
            [
                {"$group": {"_id": "$discovery_method", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]
        )
        d = [(x["_id"], x["count"]) for x in r]
        data += sorted(d, key=lambda x: -x[1])
        # Discovery jobs
        data += [SectionRow("Discovery jobs summary")]
        data += [["Box", j_box]]
        data += [["Periodic", j_periodic]]
        data += [SectionRow("Jobs per second")]
        data += [["Box", j_box_sec]]
        data += [["Periodic", j_periodic_sec]]
        return self.from_dataset(
            title=self.title,
            columns=[
                " ",
                TableColumn(
                    "Count", align="right", format="integer", total="sum", total_label="Total"
                ),
            ],
            data=data,
        )
