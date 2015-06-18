# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.reportvpnstatus
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow
from noc.ip.models import VRF
from noc.inv.models.forwardinginstance import ForwardingInstance
from noc.inv.models.subinterface import SubInterface


class ReportVPNStatusApplication(SimpleReport):
    title = "VPN Status"

    def get_data(self, **kwargs):
        data = []
        for vrf in VRF.objects.all().order_by("name"):
            if vrf.rd == "0:0":
                continue  # Skip global
            d = []
            for fi in ForwardingInstance.objects.filter(type="VRF",
                name=vrf.name):
                si = [i.name for i in
                      SubInterface.objects.filter(
                          forwarding_instance=fi.id).only("name")]
                si = sorted(si)
                if si:
                    d += [[fi.managed_object.name, ", ".join(si)]]
            if d:
                data += [SectionRow(name="VRF %s, RD: %s [%s]" % (
                    vrf.name, vrf.rd, vrf.state.name
                ))]
                data += d
        #
        return self.from_dataset(
            title=self.title,
            columns=["Managed. Object", "Interfaces"],
            data=data
        )
