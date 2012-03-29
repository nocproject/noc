# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.vrf application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.ip.models import VRF, VRFGroup
from noc.sa.interfaces import StringParameter, BooleanParameter,\
    ModelParameter, RDParameter, ListOfParameter, DictParameter


class VRFApplication(ExtModelApplication):
    """
    VRF application
    """
    title = "VRFs"
    menu = "VRFs"
    model = VRF
    query_fields = ["name", "rd", "description"]

    mrt_config = {
        "get_vrfs": {
            "map_script": "get_mpls_vpn",
            "access": "import"
        }
    }

    @view(url="^bulk/import/$", method=["POST"], access="import", api=True,
          validate={
              "items": ListOfParameter(element=DictParameter(attrs={
                  "name": StringParameter(),
                  "rd": RDParameter(),
                  "vrf_group": ModelParameter(model=VRFGroup),
                  "afi_ipv4": BooleanParameter(default=False),
                  "afi_ipv6": BooleanParameter(default=False),
                  "description": StringParameter(required=False)
              }))
          })
    def api_bulk_import(self, request, items):
        n = 0
        for i in items:
            if not VRF.objects.filter(name=i["name"], rd=i["rd"]).exists():
                # Add only new
                VRF(name=i["name"], vrf_group=i["vrf_group"], rd=i["rd"],
                    afi_ipv4=i["afi_ipv4"], afi_ipv6=i["afi_ipv6"],
                    description=i.get("description")).save()
                n += 1
        return {
            "status": True,
            "imported": n
        }