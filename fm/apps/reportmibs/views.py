# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIBs Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.fm.models import MIB, MIBData


class ReportreportMIBs(SimpleReport):
    title="Installed MIBs"
    def get_data(self,**kwargs):
        data = []  # Mib, Last Updated, Entries, Depends, Used by
        for m in MIB.objects.order_by("name"):
            ec = MIBData.objects.filter(mib=m.id).count()
            data += [[m.name, m.last_updated, ec,
                      ", ".join(m.depends_on),
                      ", ".join([x.name for x in m.depended_by])]]
        return self.from_dataset(title=self.title,
            columns=[
                TableColumn("MIB", total_label="Total:"),
                TableColumn("Last Updated", format="date"),
                TableColumn("Entries", align="right", format="integer", total="sum"),
                TableColumn("Depends on"),
                TableColumn("Used by")],
            data=data,
            enumerate=True)
