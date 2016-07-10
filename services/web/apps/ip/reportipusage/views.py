# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.reportipusage
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow, TableColumn
from noc.lib.ip import IP


class ReportIPUsageApplication(SimpleReport):
    title = "IP Usage"

    QUERY = """
    SELECT v.name, v.rd, p.afi, p.prefix, p.description, COUNT(*)
    FROM ip_vrf v JOIN ip_prefix p ON (v.id = p.vrf_id)
        JOIN ip_address a ON (p.id = a.prefix_id)
    GROUP BY 1, 2, 3, 4, 5 ORDER BY 1, 2, 3, 4"""

    def get_data(self, **kwargs):
        from django.db import connection

        data = []
        last_vrf = None
        c = connection.cursor()
        c.execute(self.QUERY)
        for vrf, rd, afi, prefix, description, used in c:
            if last_vrf != vrf:
                data += [SectionRow("%s (%s)" % (vrf, rd))]
                last_vrf = vrf
            p = IP.prefix(prefix)
            if afi == "4":
                total = p.size
                if p.mask < 31 and total - used >= 2:
                    # Exclude network and broadcast
                    total = p.size - 2
                free = total - used
                percent = used * 100 / total
            elif afi == "6":
                if p.mask >= 96:
                    total = 2 ** (128 - p.mask)
                    free = total - used
                    percent = used * 100 / total
                else:
                    total = "-"
                    free = "-"
                    percent = "-"
            data += [[prefix, description, used, free, total, percent]]
        return self.from_dataset(title=self.title,
            columns=[
                "Prefix",
                "Description",
                TableColumn("IP Used", align="right", format="numeric"),
                TableColumn("IP Free", align="right", format="numeric"),
                TableColumn("IP Total", align="right", format="numeric"),
                TableColumn("% Used", align="right", format="percent")
            ],
            data=data)
