# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# alarm datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.models.serviceprofile import ServiceProfile
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.core.datastream.base import DataStream
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.utils import get_alarm


class AlarmDataStream(DataStream):
    name = "alarm"

    clean_id = DataStream.clean_id_bson

    @classmethod
    def get_object(cls, id):
        alarm = get_alarm(id)
        if not alarm:
            raise KeyError()
        r = {
            "id": str(alarm.id),
            "timestamp": cls.qs(alarm.timestamp),
            "severity": alarm.severity,
            "reopens": alarm.reopens
        }
        if alarm.root:
            r["root"] = str(alarm.root)
        if alarm.status == "C":
            r["clear_timestamp"] = cls.qs(alarm.clear_timestamp)
        cls._apply_managed_object(alarm, r)
        cls._apply_alarm_class(alarm, r)
        cls._apply_vars(alarm, r)
        cls._apply_escalation(alarm, r)
        cls._apply_services(alarm, r)
        return r

    @classmethod
    def _apply_managed_object(cls, alarm, r):
        mo = alarm.managed_object
        r["managed_object"] = {
            "id": str(mo.id),
            "name": cls.qs(mo.name),
            "object_profile": {
                "id": str(mo.object_profile.id),
                "name": str(mo.object_profile.name)
            }
        }
        if mo.remote_system:
            r["managed_object"]["remote_system"] = {
                "id": str(mo.remote_system.id),
                "name": cls.qs(mo.remote_system.name)
            }
            r["managed_object"]["remote_id"] = mo.remote_id

    @classmethod
    def _apply_alarm_class(cls, alarm, r):
        r["alarm_class"] = {
            "id": str(alarm.alarm_class.id),
            "name": cls.qs(alarm.alarm_class.name)
        }

    @classmethod
    def _apply_vars(cls, alarm, r):
        r["vars"] = {}
        for k in alarm.vars:
            r["vars"][k] = alarm.vars[k]

    @classmethod
    def _apply_escalation(cls, alarm, r):
        if not alarm.escalation_tt:
            return
        mo = alarm.managed_object
        r["escalation"] = {
            "timestamp": cls.qs(alarm.escalation_ts),
            "tt_id": cls.qs(alarm.escalation_tt),
            "tt_system": {
                "id": str(mo.tt_system.id),
                "name": cls.qs(mo.tt_system.name)
            }
        }
        if alarm.escalation_error:
            r["escalation"]["error"] = cls.qs(alarm.escalation_error)
        if alarm.status == "C" and alarm.escalation_close_ts:
            r["escalation"]["close_timestamp"] = cls.qs(alarm.escalation_close_ts)
        if alarm.status == "C" and alarm.escalation_close_error:
            r["escalation"]["close_error"] = cls.qs(alarm.escalation_close_error)

    @classmethod
    def _apply_services(cls, alarm, r):
        cls._apply_direct_services(alarm, r)
        cls._apply_total_services(alarm, r)
        cls._apply_direct_subscribers(alarm, r)
        cls._apply_total_subscribers(alarm, r)

    @classmethod
    def _apply_direct_services(cls, alarm, r):
        r["direct_services"] = []
        for si in alarm.direct_services:
            p = ServiceProfile.get_by_id(si.profile)
            if p:
                r["direct_services"] += [{
                    "profile": {
                        "id": str(p.id),
                        "name": cls.qs(p.name)
                    },
                    "summary": si.summary
                }]

    @classmethod
    def _apply_total_services(cls, alarm, r):
        r["total_services"] = []
        for si in alarm.total_services:
            p = ServiceProfile.get_by_id(si.profile)
            if p:
                r["total_services"] += [{
                    "profile": {
                        "id": str(p.id),
                        "name": cls.qs(p.name)
                    },
                    "summary": si.summary
                }]

    @classmethod
    def _apply_direct_subscribers(cls, alarm, r):
        r["direct_subscribers"] = []
        for si in alarm.direct_subscribers:
            p = SubscriberProfile.get_by_id(si.profile)
            if p:
                r["direct_subscribers"] += [{
                    "profile": {
                        "id": str(p.id),
                        "name": cls.qs(p.name)
                    },
                    "summary": si.summary
                }]

    @classmethod
    def _apply_total_subscribers(cls, alarm, r):
        r["total_subscribers"] = []
        for si in alarm.total_subscribers:
            p = SubscriberProfile.get_by_id(si.profile)
            if p:
                r["total_subscribers"] += [{
                    "profile": {
                        "id": str(p.id),
                        "name": cls.qs(p.name)
                    },
                    "summary": si.summary
                }]

    @classmethod
    def get_meta(cls, data):
        return {
            "alarmclass": data["alarm_class"]["id"]
        }

    @classmethod
    def filter_alarmclass(cls, *args):
        ids = [str(AlarmClass.get_by_name(a).id) for a in args if AlarmClass.get_by_name(a)]
        if len(ids) == 1:
            return {
                "%s.alarmclass" % cls.F_META: ids[0]
            }
        else:
            return {
                "%s.alarmclass" % cls.F_META: {
                    "$in": ids
                }
            }
