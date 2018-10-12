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
            "id", "bi_id", "is_managed", "pool", "address", "syslog_source_ip", "syslog_source_type",
            "event_processing_policy", "object_profile__event_processing_policy",
            "syslog_archive_policy", "object_profile__syslog_archive_policy")[:1]
        if not mo:
            raise KeyError()
        (mo_id, bi_id, is_managed, pool, address, syslog_source_ip, syslog_source_type,
         event_processing_policy, mop_event_processing_policy,
         syslog_archive_policy, mop_syslog_archive_policy) = mo[0]
        # Check if object capable to receive syslog events
        if not is_managed or str(syslog_source_type) == "d":
            raise KeyError()
        # Get effective event processing policy
        event_processing_policy = str(event_processing_policy)
        mop_event_processing_policy = str(mop_event_processing_policy)
        effective_epp = event_processing_policy == "E" or (
            event_processing_policy == "P" and mop_event_processing_policy == "E")
        # Get effective event archiving policy
        syslog_archive_policy = str(syslog_archive_policy)
        mop_syslog_archive_policy = str(mop_syslog_archive_policy)
        effective_sap = syslog_archive_policy == "E" or (
            syslog_archive_policy == "P" and mop_syslog_archive_policy == "E")
        # Check syslog events may be processed
        if not effective_epp and not effective_sap:
            raise KeyError()
        # Process syslog sources
        r = {
            "id": str(mo_id),
            "bi_id": str(bi_id),
            "pool": str(Pool.get_by_id(pool).name),
            "addresses": [],
            "process_events": effective_epp,
            "archive_events": effective_sap
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
