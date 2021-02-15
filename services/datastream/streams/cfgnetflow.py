# ----------------------------------------------------------------------
# cfgnetflow datastream
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.base import DataStream
from noc.sa.models.managedobject import ManagedObject


class CfgNetflowDataStream(DataStream):
    name = "cfgnetflow"
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        mo = ManagedObject.objects.filter(id=id).values_list(
            "id",
            "bi_id",
            "address",
        )[:1]
        if not mo:
            raise KeyError()
        (
            mo_id,
            bi_id,
            address,
        ) = mo[0]
        r = {
            "id": str(mo_id),
            "bi_id": str(bi_id),
            "addresses": [],
        }

        addresses = cls._get_all_addresses(mo_id)
        addresses.add(str(address))
        r["addresses"] = [x for x in addresses if x != "127.0.0.1"]
        if not r["addresses"]:
            raise KeyError()

        return r

    @classmethod
    def _get_all_addresses(cls, mo_id):
        from noc.inv.models.subinterface import SubInterface

        r = []
        for d in SubInterface._get_collection().find(
            {"managed_object": int(mo_id), "ipv4_addresses": {"$exists": True}}, {"ipv4_addresses"}
        ):
            for a in d.get("ipv4_addresses", []):
                r += [str(a).split("/")[0]]
        return set(r)
