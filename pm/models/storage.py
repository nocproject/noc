## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PMStrorage model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from noc.lib.nosql import (Document, StringField,
                           IntField, PlainReferenceField)
from db import PMDatabase


class PMStorage(Document):
    """
    Storage for PM data. Data are stored in collections
    `collection`.raw
    `collection`.l0
    ...
    `collection`.lN
    """
    meta = {
        "collection": "noc.pm.storage",
        "allow_inheritance": False
    }

    # Storate name
    name = StringField(unique=True)
    # Database
    db = PlainReferenceField(PMDatabase)
    # Collection prefix
    collection = StringField()
    # Store unaggregated data `raw_retention` seconds
    raw_retention = IntField(default=86400)

    TIME_SERIES_ID = "s"
    VALUE = "v"

    CHUNK = 1000

    def __unicode__(self):
        return self.name

    def prepare(self):
        """
        Initialize collection and prepare indexes
        :return:
        """
        c = self.get_raw_collection()
        c.ensure_index(self.TIME_SERIES_ID)

    def get_raw_collection(self):
        """
        Get collection for raw data
        :return:
        """
        c = getattr(self, "_pmcraw", None)
        if c:
            return c
        cn = self.collection + ".raw"
        db = self.db.get_database()
        c = db[cn]
        self._pmcraw = c
        return c

    def get_object_id(self, timestamp, ts=0):
        return (long(timestamp) << 32) | long(ts)

    def object_id_to_timestamp(self, o):
        return o >> 32

    def register(self, data):
        """
        Bulk register series of data
        :param data: List of ts_id, timestamp, value
        :return:
        """
        c = self.get_raw_collection()
        for chunk in [data[i:i + self.CHUNK]
                      for i in range(0, len(data), self.CHUNK)]:
            c.insert(
                [
                    {
                        "_id": self.get_object_id(timestamp, ts),
                        self.TIME_SERIES_ID: int(ts),
                        self.VALUE: value
                    } for ts, timestamp, value in chunk
                ], w=0, j=False)

    @property
    def stats(self):
        return self.get_raw_collection().stats()

    def iwindow(self, t0, t1, tses):
        """
        :param t0: Start timestamp
        :param t1: End timestamp
        :param tses: List of timeseries ids
        :return: yields ts id, timestamp, value
        """
        q = {
            "_id": {
                "$gt": self.get_object_id(t0, 0),
                "$lt": self.get_object_id(t1, 0xFFFFFFFF)
            }
        }
        if isinstance(tses, (int, long)):
            q[self.TIME_SERIES_ID] = tses
        else:
            q[self.TIME_SERIES_ID] = {"$in": tses}
        for doc in self.get_raw_collection().find(q):
            yield (
                doc[self.TIME_SERIES_ID],
                self.object_id_to_timestamp(doc["_id"]),
                doc[self.VALUE]
            )
