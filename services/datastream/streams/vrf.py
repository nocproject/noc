# ----------------------------------------------------------------------
# vrf datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.base import DataStream
from ..models.vrf import VRFGroupDataStreamItem
from noc.ip.models.vrf import VRF
from noc.core.comp import smart_text


def qs(s):
    if not s:
        return ""
    return smart_text(s)


class VRFGroupDataStream(DataStream):
    name = "vrf"
    model = VRFGroupDataStreamItem
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        vrf = VRF.objects.filter(id=id).first()
        if not vrf:
            raise KeyError()
        r = {
            "id": str(vrf.id),
            "name": qs(vrf.name),
            "vpn_id": vrf.vpn_id,
            "afi": {"ipv4": vrf.afi_ipv4, "ipv6": vrf.afi_ipv6},
            "source": vrf.source,
        }
        if vrf.description:
            r["description"] = str(vrf.description)
        if vrf.rd:
            r["rd"] = str(vrf.rd)
        if vrf.labels:
            r["labels"] = [qs(x) for x in vrf.labels]
            # Alias for compat
            r["tags"] = [qs(x) for x in vrf.labels]
        cls._apply_state(vrf, r)
        cls._apply_profile(vrf, r)
        cls._apply_project(vrf, r)
        return r

    @staticmethod
    def _apply_state(vrf, r):
        r["state"] = {
            "id": str(vrf.state.id),
            "name": qs(vrf.state.name),
            "workflow": {"id": str(vrf.state.workflow.id), "name": qs(vrf.state.workflow.name)},
        }
        if vrf.allocated_till:
            r["state"]["allocated_till"] = vrf.allocated_till.isoformat()

    @staticmethod
    def _apply_profile(vrf, r):
        r["profile"] = {"id": str(vrf.profile.id), "name": qs(vrf.profile.name)}

    @staticmethod
    def _apply_project(vrf, r):
        if not vrf.project:
            return
        r["project"] = {"id": str(vrf.project.id), "name": qs(vrf.project.name)}
