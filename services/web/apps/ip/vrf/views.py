# ---------------------------------------------------------------------
# ip.vrf application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication, view
from noc.ip.models.vrfgroup import VRFGroup
from noc.ip.models.vrf import VRF
from noc.sa.interfaces.base import (
    StringParameter,
    BooleanParameter,
    ModelParameter,
    RDParameter,
    ListOfParameter,
    DictParameter,
)
from noc.core.translation import ugettext as _
from noc.core.vpn import get_vpn_id
from noc.services.web.base.decorators.state import state_handler


@state_handler
class VRFApplication(ExtModelApplication):
    """
    VRF application
    """

    title = _("VRF")
    menu = _("VRF")
    model = VRF
    query_fields = ["name", "rd", "description"]

    mrt_config = {"get_vrfs": {"map_script": "get_mpls_vpn", "access": "import"}}

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile.style else ""

    def clean(self, data):
        if not data.get("vpn_id"):
            vdata = {"type": "VRF", "name": data["name"], "rd": data.get("rd")}
            data["vpn_id"] = get_vpn_id(vdata)
        return super().clean(data)

    @view(
        url="^bulk/import/$",
        method=["POST"],
        access="import",
        api=True,
        validate={
            "items": ListOfParameter(
                element=DictParameter(
                    attrs={
                        "name": StringParameter(),
                        "rd": RDParameter(),
                        "vrf_group": ModelParameter(model=VRFGroup),
                        "afi_ipv4": BooleanParameter(default=False),
                        "afi_ipv6": BooleanParameter(default=False),
                        "description": StringParameter(required=False),
                    }
                )
            )
        },
    )
    def api_bulk_import(self, request, items):
        n = 0
        for i in items:
            if not VRF.objects.filter(name=i["name"], rd=i["rd"]).exists():
                # Add only new
                VRF(
                    name=i["name"],
                    vrf_group=i["vrf_group"],
                    rd=i["rd"],
                    afi_ipv4=i["afi_ipv4"],
                    afi_ipv6=i["afi_ipv6"],
                    description=i.get("description"),
                ).save()
                n += 1
        return {"status": True, "imported": n}
