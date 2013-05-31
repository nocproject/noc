## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VLAN Discovery Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import Report
from noc.settings import config
from noc.vc.models.vc import VC


class VLANReport(Report):
    system_notification = "inv.vlan_discovery"

    def __init__(self, job, enabled=True, to_save=False):
        super(VLANReport, self).__init__(
            job, enabled=enabled, to_save=to_save)
        self.vc_state_map = self.get_state_map(
            config.get("vlan_discovery", "change_state"))
        self.new_vcs = []

    def submit(self, vc_domain, l1, name=None):
        if not self.enabled:
            return
        r = vc_domain.vc_set.filter(l1=l1)
        if r:
            self.change_vc(r[0])
        else:
            self.new_vc(vc_domain, l1, name)

    def change_vc(self, vc):
        """
        Change VC state according change_state map
        :param vc:
        :return:
        """
        if vc.state.id in self.vc_state_map:
            fs = vc.state
            ts = self.vc_state_map[fs.id]
            self.info("Changing VC state: %s %s -> %s" % (
                vc, fs, ts))
            if self.to_save:
                vc.state = ts
                vc.save()

    def new_vc(self, vc_domain, l1, name):
        """
        Create new VC
        :param vc_domain:
        :param l1:
        :param name:
        :return:
        """
        self.new_vcs += [{
            "vc_domain": vc_domain,
            "l1": l1,
            "name": name
        }]
        if self.to_save:
            vc = VC(
                vc_domain=vc_domain,
                name=name,
                l1=l1, l2=0
            )
            vc.save()

    def send(self):
        if not self.new_vcs:
            pass
        # Send report
        ctx = {
            "count": len(self.new_vcs),
            "vcs": self.new_vcs
        }
        self.notify("inv.discovery.new_vlans_report", ctx)
