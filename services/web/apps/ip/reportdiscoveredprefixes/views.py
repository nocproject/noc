# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Discovered Prefixes Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from noc.core.translation import ugettext as _

# NOC Modules
from noc.lib.app.simplereport import SimpleReport
from noc.inv.models.newprefixdiscoverylog import NewPrefixDiscoveryLog


class ReportDiscoveredPrefixes(SimpleReport):
    title = _("Discovered Prefixes")

    def get_data(self, **kwargs):
        data = [
            (p.timestamp, p.vrf, p.prefix, p.description, p.managed_object, p.interface)
            for p in NewPrefixDiscoveryLog.objects.order_by("-timestamp")
        ]

        return self.from_dataset(
            title="Discovered Prefixes",
            columns=["Timestamp", "VRF", "Prefix", "Description", "Object", "Interface"],
            data=data,
        )
