# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vlan check
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.vc.models.vc import VC


class VLANCheck(DiscoveryCheck):
    """
    VLAN discovery
    """
    name = "vlan"
    required_script = "get_vlans"

    def handler(self):
        self.logger.info("Checking vlans")
        if not self.object.vc_domain:
            self.logger.info(
                "No vc domain. Skipping"
            )
            return
        result = self.object.get_vlans()
        for v in result:
            self.submit(
                vc_domain=self.object.vc_domain,
                l1=v["vlan_id"],
                name=v.get("name")
            )

    def submit(self, vc_domain, l1, name=None):
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
        pass

    def new_vc(self, vc_domain, l1, name):
        """
        Create new VC
        :param vc_domain:
        :param l1:
        :param name:
        :return:
        """
        if not name:
            name = "VLAN_%d" % l1
        # Check constraints
        while vc_domain.vc_set.filter(name=name).count() > 0:
            name += "_"
        vc = VC(
            vc_domain=vc_domain,
            name=name,
            l1=l1, l2=0
        )
        vc.save()
