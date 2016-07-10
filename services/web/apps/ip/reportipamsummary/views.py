# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.reportipamsummary
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn


class ReportIPAMSummaryApplication(SimpleReport):
    title = "IPAM Summary"

    def get_data(self, **kwargs):
        return self.from_query(
            title="IPAM Summary",
            columns=[
                "VRF", "RD",
                TableColumn("Prefixes", align="right",
                            format="integer", total="sum"),
                TableColumn("Addresses", align="right",
                            format="integer", total="sum")
            ],
            query="""
                SELECT vrf.name, vrf.rd,
                       (SELECT COUNT(*) FROM ip_prefix
                        WHERE vrf_id=vrf.id) AS prefixes,
                       (SELECT COUNT(*) FROM ip_address
                        WHERE vrf_id=vrf.id) AS addresses
                FROM ip_vrf vrf
                ORDER BY 1
            """,
            enumerate=True
        )
