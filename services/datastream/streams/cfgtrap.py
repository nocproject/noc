# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# cfgtrap datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.base import DataStream
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject


class CfgTrapDataStream(DataStream):
    name = "cfgtrap"
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        mo = ManagedObject.objects.filter(id=id).values_list(
            "id", "is_managed", "pool", "address", "trap_community", "trap_source_ip", "trap_source_type",
            "event_processing_policy", "object_profile__event_processing_policy")[:1]
        if not mo:
            raise KeyError()
        (mo_id, is_managed, pool, address, trap_community, trap_source_ip, trap_source_type,
         event_processing_policy, mop_event_processing_policy) = mo[0]
        # Process event policy
        if not is_managed or (str(event_processing_policy) == "P" and str(mop_event_processing_policy) != "E") or \
                str(event_processing_policy) == "D" or str(trap_source_type) == "d":
            raise KeyError()
        # Process trap sources
        r = {
            "id": str(mo_id),
            "pool": str(Pool.get_by_id(pool).name),
            "addresses": [],
            "trap_community": trap_community
        }
        if str(trap_source_type) == "m" and address:
            r["addresses"] += [str(address)]
        elif str(trap_source_type) == "s" and trap_source_ip:
            r["addresses"] = [str(trap_source_ip)]
        elif trap_source_type== "l":
            # Loopback address
            r["addresses"] = cls._get_loopback_addresses(mo_id)
            if not r["addresses"]:
                raise KeyError()
        elif trap_source_type == "a":
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
        for d in Interface._get_collection().find({
            "managed_object": int(mo_id),
            "type": "loopback"
        }, {
            "_id": 1
        }):
            if_ids += [d["_id"]]
        if not if_ids:
            return []
        # Get loopback's addresses
        r = []
        for d in SubInterface._get_collection().find({
            "managed_object": int(mo_id),
            "interface": {
                "$in": if_ids
            },
            "ipv4_addresses": {
                "$exists": True
            }
        }, {
            "_id": 0,
            "ipv4_addresses":1
        }):
            for a in d.get("ipv4_addresses", []):
                r += [str(a).split("/")[0]]
        return r

    @classmethod
    def _get_all_addresses(cls, mo_id):
        from noc.inv.models.subinterface import SubInterface
        r = []
        for d in SubInterface._get_collection().find({
            "managed_object": int(mo_id),
            "ipv4_addresses": {
                "$exists": True
            }
        }, {
            "ipv4_addresses"
        }):
            for a in d.get("ipv4_addresses", []):
                r += [str(a).split("/")[0]]
        return r

    @classmethod
    def get_meta(cls, data):
        return {
            "pool": data.get("pool")
        }

    @classmethod
    def filter_pool(cls, name):
        return {
            "%s.pool" % cls.F_META: name
        }
