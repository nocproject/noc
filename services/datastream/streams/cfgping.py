# ----------------------------------------------------------------------
# cfgping datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.base import DataStream
from noc.main.models.pool import Pool
from noc.main.models.timepattern import TimePattern
from noc.sa.models.managedobject import ManagedObject


class CfgPingDataStream(DataStream):
    name = "cfgping"
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        mo = ManagedObject.objects.filter(id=id).values_list(
            "id",
            "name",
            "bi_id",
            "is_managed",
            "pool",
            "fm_pool",
            "address",
            "time_pattern",
            "object_profile__enable_ping",
            "object_profile__ping_interval",
            "object_profile__ping_policy",
            "object_profile__ping_size",
            "object_profile__ping_count",
            "object_profile__ping_timeout_ms",
            "object_profile__ping_time_expr_policy",
            "object_profile__report_ping_rtt",
            "object_profile__report_ping_attempts",
        )[:1]
        if not mo:
            raise KeyError()
        (
            mo_id,
            name,
            bi_id,
            is_managed,
            pool,
            fm_pool,
            address,
            time_pattern,
            enable_ping,
            ping_interval,
            ping_policy,
            ping_size,
            ping_count,
            ping_timeout_ms,
            ping_time_expr_policy,
            report_ping_rtt,
            report_ping_attempts,
        ) = mo[0]
        if (
            not is_managed
            or not address
            or not enable_ping
            or not ping_interval
            or ping_interval < 0
        ):
            raise KeyError()
        pool = str(Pool.get_by_id(pool).name)
        r = {
            "id": str(mo_id),
            "pool": pool,
            "fm_pool": str(Pool.get_by_id(fm_pool).name) if fm_pool else pool,
            "address": str(address),
            "interval": ping_interval,
            "policy": ping_policy,
            "size": ping_size,
            "count": ping_count,
            "timeout": ping_timeout_ms,
            "expr_policy": ping_time_expr_policy,
            "report_rtt": report_ping_rtt,
            "report_attempts": report_ping_attempts,
            "status": None,
            "name": name,
            "bi_id": bi_id,
        }
        if time_pattern:
            r["time_expr"] = TimePattern.get_code(time_pattern)
        return r

    @classmethod
    def get_meta(cls, data):
        return {"pool": data.get("pool")}

    @classmethod
    def filter_pool(cls, name):
        return {"%s.pool" % cls.F_META: name}
