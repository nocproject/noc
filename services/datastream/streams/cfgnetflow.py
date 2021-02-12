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
            "syslog_source_ip",
            "syslog_source_type",
        )[:1]
        if not mo:
            raise KeyError()
        (
            mo_id,
            bi_id,
            address,
            syslog_source_ip,
            syslog_source_type,
        ) = mo[0]
        r = {
            "id": str(mo_id),
            "bi_id": str(bi_id),
            "addresses": [],
        }

        if syslog_source_type == "m" and address:
            # Managed Object's address
            r["addresses"] += [str(address)]
        elif syslog_source_type == "s" and syslog_source_ip:
            # Syslog source set manually
            r["addresses"] = [str(syslog_source_ip)]
        elif syslog_source_type == "l":
            # Loopback address
            r["addresses"] = cls._get_loopback_addresses(mo_id)
            if not r["addresses"]:
                raise KeyError()
        elif syslog_source_type == "a":
            # All interface addresses
            r["addresses"] = cls._get_all_addresses(mo_id)
            if not r["addresses"]:
                raise KeyError()
        else:
            raise KeyError()

        return r

    @classmethod
    def _get_loopback_addresses(cls, mo_id):
        from noc.inv.models.interface import Interface
        from noc.inv.models.subinterface import SubInterface

        # Get all loopbacks
        if_ids = []
        for d in Interface._get_collection().find(
            {"managed_object": int(mo_id), "type": "loopback"}, {"_id": 1}
        ):
            if_ids += [d["_id"]]
        if not if_ids:
            return []
        # Get loopback's addresses
        r = []
        for d in SubInterface._get_collection().find(
            {
                "managed_object": int(mo_id),
                "interface": {"$in": if_ids},
                "ipv4_addresses": {"$exists": True},
            },
            {"_id": 0, "ipv4_addresses": 1},
        ):
            for a in d.get("ipv4_addresses", []):
                r += [str(a).split("/")[0]]
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
        return r
