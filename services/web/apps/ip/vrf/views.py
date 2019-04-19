# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.vrf application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.contrib.auth.models import User, Group
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.ip.models.vrfgroup import VRFGroup
from noc.ip.models.vrf import VRF
from noc.sa.interfaces.base import (StringParameter, BooleanParameter,
                                    ModelParameter, RDParameter,
                                    ListOfParameter, DictParameter)
from noc.core.translation import ugettext as _
from noc.core.vpn import get_vpn_id
from noc.lib.app.decorators.state import state_handler


@state_handler
class VRFApplication(ExtModelApplication):
    """
    VRF application
    """
    title = _("VRF")
    menu = _("VRF")
    model = VRF
    query_fields = ["name", "rd", "description"]

    mrt_config = {
        "get_vrfs": {
            "map_script": "get_mpls_vpn",
            "access": "import"
        }
    }

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile.style else ""

    def clean(self, data):
        if not data.get("vpn_id"):
            vdata = {
                "type": "VRF",
                "name": data["name"],
                "rd": data.get("rd")
            }
            data["vpn_id"] = get_vpn_id(vdata)
        if data.get("direct_permissions"):
            data["direct_permissions"] = [[x["user"], x["group"], x["permission"]] for x in data["direct_permissions"]]
        return super(VRFApplication, self).clean(data)

    @view(
        url="^bulk/import/$", method=["POST"], access="import",
        api=True,
        validate={
            "items": ListOfParameter(element=DictParameter(attrs={
                "name": StringParameter(),
                "rd": RDParameter(),
                "vrf_group": ModelParameter(model=VRFGroup),
                "afi_ipv4": BooleanParameter(default=False),
                "afi_ipv6": BooleanParameter(default=False),
                "description": StringParameter(required=False)
            }))
        }
    )
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

    def instance_to_dict(self, o, fields=None):
        r = super(VRFApplication, self).instance_to_dict(o, fields=fields)
        r["direct_permissions"] = []
        if o.direct_permissions:
            for user, group, perm in o.direct_permissions:
                user = User.objects.get(id=user)
                group = Group.objects.get(id=group)
                r["direct_permissions"] += [{
                    "user": user.id,
                    "user__label": user.username,
                    "group": group.id,
                    "group__label": group.name,
                    "permission": perm
                }]
        return r
