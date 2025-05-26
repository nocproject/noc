# ----------------------------------------------------------------------
# prefix datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.base import DataStream
from noc.ip.models.prefix import Prefix
from ..models.prefix import PrefixDataStreamItem
from noc.core.comp import smart_text


def qs(s):
    if not s:
        return ""
    return smart_text(s)


class PrefixDataStream(DataStream):
    name = "prefix"
    model = PrefixDataStreamItem
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        prefix = Prefix.objects.filter(id=id).first()
        if not prefix:
            raise KeyError()
        r = {
            "id": str(prefix.id),
            "name": qs(prefix.name),
            "prefix": qs(prefix.prefix),
            "afi": "ipv%s" % prefix.afi,
            "source": prefix.source,
        }
        if prefix.description:
            r["description"] = str(prefix.description)
        if prefix.labels:
            r["labels"] = [qs(x) for x in prefix.labels]
            # Alias for compat
            r["tags"] = [qs(x) for x in prefix.labels]
        if prefix.tt:
            r["tt"] = prefix.tt
        cls._apply_state(prefix, r)
        cls._apply_profile(prefix, r)
        cls._apply_vrf(prefix, r)
        cls._apply_asn(prefix, r)
        cls._apply_project(prefix, r)
        return r

    @staticmethod
    def _apply_state(prefix, r):
        r["state"] = {
            "id": str(prefix.state.id),
            "name": qs(prefix.state.name),
            "workflow": {
                "id": str(prefix.state.workflow.id),
                "name": qs(prefix.state.workflow.name),
            },
        }
        if prefix.allocated_till:
            r["state"]["allocated_till"] = prefix.allocated_till.isoformat()

    @staticmethod
    def _apply_profile(prefix, r):
        r["profile"] = {"id": str(prefix.profile.id), "name": qs(prefix.profile.name)}

    @staticmethod
    def _apply_project(prefix, r):
        if not prefix.project:
            return
        r["project"] = {"id": str(prefix.project.id), "name": qs(prefix.project.name)}

    @staticmethod
    def _apply_vrf(prefix, r):
        if not prefix.vrf or prefix.vrf.is_global:
            return
        r["vrf"] = {"id": str(prefix.vrf.id), "name": str(prefix.vrf.name)}

    @staticmethod
    def _apply_asn(prefix, r):
        if not prefix.asn or not prefix.asn.asn:
            return
        r["as"] = {
            "id": str(prefix.asn.id),
            "name": str(prefix.asn.as_name),
            "as": "AS%d" % prefix.asn.asn,
        }

    @classmethod
    def get_meta(cls, data):
        if not data:
            return
        return {"vrf": data["vrf"]["id"]}

    @classmethod
    def filter_vrf(cls, vid):
        return {f"{cls.F_META}.vrf": int(vid)}
