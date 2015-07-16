# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovered Addresses Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC Modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.inv.models.newaddressdiscoverylog import NewAddressDiscoveryLog


class ReportDiscoveredAddreses(SimpleReport):
    title = "Discovered Addresses"

    def get_data(self, **kwargs):
        data = [
            (
                p.timestamp, p.vrf, p.address, p.description,
                p.managed_object, p.interface
            ) for p in
              NewAddressDiscoveryLog.objects.order_by("-timestamp")
        ]

        return self.from_dataset(
            title="Discovered Addresses",
            columns=[
                "Timestamp",
                "VRF",
                "Address",
                "Description",
                "Object",
                "Interface"
            ],
            data=data)
