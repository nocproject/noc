# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# cfgping datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.base import DataStream
from noc.main.models.timepattern import TimePattern
from noc.sa.models.managedobject import ManagedObject


class CfgPingDataStream(DataStream):
    name = "cfgping"
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        mo = ManagedObject.objects.filter(id=id)[:1]
        if not mo:
            raise KeyError()
        mo = mo[0]
        if mo.address and mo.object_profile.ping_interval and mo.object_profile.ping_interval > 0:
            r = {
                "id": str(mo.id),
                "pool": str(mo.pool.name),
                "interval": mo.object_profile.ping_interval,
                "policy": mo.object_profile.ping_policy,
                "size": mo.object_profile.ping_size,
                "count": mo.object_profile.ping_count,
                "timeout": mo.object_profile.ping_timeout_ms,
                "report_rtt": mo.object_profile.report_ping_rtt,
                "report_attempts": mo.object_profile.report_ping_attempts,
                "status": None,
                "name": mo.name,
                "bi_id": mo.bi_id
            }
            if mo.time_pattern:
                r["time_expr"] = TimePattern.get_code(mo.time_pattern.id)
            return r
        else:
            raise KeyError()

    @classmethod
    def get_meta(cls, data):
        return {
            "pool": data.get("pool")
        }
