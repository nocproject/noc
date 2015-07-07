# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MongoDB Key-Value storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from bson.binary import Binary
## NOC modules
from base import KVStorage
from noc.lib.nosql import get_db


class MongoDBStorage(KVStorage):
    name = "mongodb"

    def __init__(self, database, partition):
        super(MongoDBStorage, self).__init__(database, partition)
        self.collection = self.get_collection(partition)

    def write(self, batch):
        """
        Batch save the data
        batch is a list of [(key, value), ...]
        """
        self.collection.insert(
            [
                {
                    "_id": Binary(key),
                    "v": Binary(value)
                } for key, value in batch
            ],
            w=0
        )

    def iterate(self, start, end):
        """
        Iterate all keys between k0 and k1
        """
        for row in self.collection.find(
            {
                "_id": {
                    "$gte": Binary(start),
                    "$lte": Binary(end)
                }
            }, {
                "_id": 1,
                "v": 1
            }
        ).sort("_id", 1):
            yield row["_id"], row["v"]

    def get_collection(self, partition):
        p = ".".join("p%s" % x for x in partition.split("."))
        db = get_db()
        return db["noc.ts.%s" % p]

    def get_last_value(self, start, end):
        d = self.collection.find(
            {
                "_id": {
                    "$gte": Binary(start),
                    "$lte": Binary(end)
                }
            }, {
                "_id": 1,
                "v": 1
            }
        ).sort("_id", -1).first()
        if d:
            return d["_id"], d["v"]
        else:
            return None, None

