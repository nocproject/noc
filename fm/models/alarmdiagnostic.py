# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlarmDiagnostic model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import zlib

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ObjectIdField, DateTimeField, BinaryField
import bson

# NOC modules
from noc.core.comp import smart_bytes


class AlarmDiagnostic(Document):
    meta = {
        "collection": "noc.alarmdiagnostic",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["alarm"],
    }

    alarm = ObjectIdField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    expires = DateTimeField()
    state = StringField(choices=[("R", "On Raise"), ("C", "On Clear"), ("P", "On Periodic")])
    data = BinaryField()

    TTL = datetime.timedelta(days=14)

    @classmethod
    def save_diagnostics(cls, alarm, diag, state):
        data = zlib.compress(b"\n\n".join(smart_bytes(d) for d in diag), 9)
        if state == "C":
            expires = datetime.datetime.now() + cls.TTL
        else:
            expires = None
        AlarmDiagnostic(alarm=alarm.id, state=state, data=bson.Binary(data), expires=expires).save()

    @classmethod
    def get_diagnostics(cls, alarm):
        if hasattr(alarm, "id"):
            alarm = alarm.id
        r = []
        for d in AlarmDiagnostic.objects.filter(alarm=alarm).order_by("timestamp"):
            r += [
                {
                    "timestamp": d.timestamp,
                    "state": d.state,
                    "data": zlib.decompress(smart_bytes(d.data)),
                }
            ]
        return r

    @classmethod
    def clear_diagnostics(cls, alarm):
        if hasattr(alarm, "id"):
            alarm = alarm.id
        AlarmDiagnostic._get_collection().update_many(
            {"alarm": alarm}, {"$set": {"expires": datetime.datetime.now() + cls.TTL}}
        )
