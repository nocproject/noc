# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# cfgtrap datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.base import DataStream
from noc.sa.models.managedobject import ManagedObject


class CfgTrapDataStream(DataStream):
    name = "cfgtrap"
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        mo = ManagedObject.objects.filter(id=id)[:1]
        if not mo:
            raise KeyError()
        mo = mo[0]
        # Process event policy
        if mo.get_event_processing_policy() != "E" or mo.trap_source_type == "d":
            raise KeyError()
        # Process trap sources
        r = {
            "id": str(mo.id),
            "pool": str(mo.pool.name),
            "addresses": []
        }
        if mo.trap_source_type == "m" and mo.address:
            r["addresses"] += [mo.address]
        elif mo.trap_source_type == "s" and mo.trap_source_ip:
            r["addresses"] = [mo.trap_source_ip]
        else:
            raise KeyError()
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
