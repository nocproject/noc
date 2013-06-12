## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PMTS model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import time
## NOC Modules
from noc.lib.nosql import (Document, StringField, IntField,
                           BooleanField, PlainReferenceField,
                           IntSequence)
from storage import PMStorage
from check import PMCheck


## TS id
seq_ts = IntSequence("pm.ts")


class PMTS(Document):
    """
    Time Series
    """
    meta = {
        "collection": "noc.pm.ts",
        "allow_inheritance": False
    }

    ts_id = IntField(primary_key=True, default=seq_ts.next)
    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    storage = PlainReferenceField(PMStorage)
    check = PlainReferenceField(PMCheck)
    type = StringField(
        default="G",
        choices=[
            ("G", "GAUGE"),
            ("C", "COUNTER"),
            ("D", "DERIVE")
        ]
    )

    def __unicode__(self):
        return self.name

    def register(self, timestamp, value):
        if isinstance(timestamp, datetime.datetime):
            timestamp = time.mktime(timestamp.timetuple())
        self.storage.register([self.ts_id, timestamp, value])

    def iwindow(self, t0, t1):
        if isinstance(t0, datetime.datetime):
            t0 = time.mktime(t0.timetuple())
        if isinstance(t1, datetime.datetime):
            t1 = time.mktime(t1.timetuple())
        return self.storage.iwindow(t0, t1, self.ts_id)

    @property
    def last_measure(self):
        """
        Returns
        :return: timestamp, value
        """
        return self.storage.get_last_measure(self.ts_is)
