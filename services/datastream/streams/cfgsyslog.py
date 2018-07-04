# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# cfgsyslog datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.base import DataStream
from noc.sa.models.managedobject import ManagedObject


class CfgSyslogDataStream(DataStream):
    name = "cfgsyslog"
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        mo = ManagedObject.objects.filter(id=id)[:1]
        if not mo:
            raise KeyError()
        mo = mo[0]
        # Process event policy
        if mo.get_event_processing_policy() != "E" or mo.syslog_source_type == "d":
            raise KeyError()
        # Process syslog sources
        r = {
            "id": str(mo.id),
            "pool": str(mo.pool.name),
            "addresses": []
        }
        if mo.syslog_source_type == "m" and mo.address:
            r["addresses"] += [mo.address]
        elif mo.syslog_source_type == "s" and mo.syslog_source_ip:
            r["addresses"] = [mo.syslog_source_ip]
        else:
            raise KeyError()

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
