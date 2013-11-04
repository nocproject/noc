## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Full-text search queue
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import (Document, StringField)


class FTSQueue(Document):
    meta = {
        "collection": "noc.fts_queue",
        "allow_inheritance": False
    }

    object = StringField(unique=True)  # <module>.<Model>:<id>
    op = StringField(choices=[("U", "Update"), ("D", "Delete")])

    def unicode(self):
        return "%s:%s" % (self.object, self.op)

    @classmethod
    def schedule_update(cls, o):
        oid = cls.get_id(o)
        cls._get_collection().update(
            {
                "object": oid
            }, {
                "$set": {
                    "object": oid,
                    "op": "U"
                }
            },
            upsert=True
        )
        cls.schedule_job()

    @classmethod
    def schedule_delete(cls, o):
        oid = cls.get_id(o)
        cls._get_collection().update(
            {
                "object": oid
            }, {
                "$set": {
                    "object": oid,
                    "op": "D"
                }
            },
            upsert=True
        )
        cls.schedule_job()

    @classmethod
    def schedule_job(cls):
        # sliding_job("main.jobs", "main.update_index",
        #            delta=5, cutoff_delta=15)
        pass

    @classmethod
    def get_id(cls, o):
        return "%s:%s" % (o._meta, o.id)
