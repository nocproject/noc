# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# cfgsyslog datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.base import DataStream
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject


class CfgSyslogDataStream(DataStream):
    name = "cfgsyslog"
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        mo = ManagedObject.objects.filter(id=id).values_list(
            "id", "is_managed", "pool", "address", "syslog_source_ip", "syslog_source_type",
            "event_processing_policy", "object_profile__event_processing_policy")[:1]
        if not mo:
            raise KeyError()
        (mo_id, is_managed, pool, address, syslog_source_ip, syslog_source_type,
         event_processing_policy, mop_event_processing_policy) = mo[0]
        # Process event policy
        if not is_managed or (str(event_processing_policy) == "P" and str(mop_event_processing_policy) != "E") or \
                str(event_processing_policy) == "D" or str(syslog_source_type) == "d":
            raise KeyError()
        # Process syslog sources
        r = {
            "id": str(mo_id),
            "pool": str(Pool.get_by_id(pool).name),
            "addresses": []
        }
        if syslog_source_type == "m" and address:
            r["addresses"] += [str(address)]
        elif syslog_source_type == "s" and syslog_source_ip:
            r["addresses"] = [str(syslog_source_ip)]
        elif str(syslog_source_type) == "l" or str(syslog_source_type) == "a":
            # Not implemented yet
            raise KeyError()
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
