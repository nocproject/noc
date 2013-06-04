## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PMDatabase model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from pymongo import MongoClient
## NOC Modules
from noc.lib.nosql import Document, StringField, IntField


class PMDatabase(Document):
    """
    Database cluster for performance data
    """
    meta = {
        "collection": "noc.pm.db",
        "allow_inheritance": False
    }

    name = StringField(unique=True)
    host = StringField()
    port = IntField()
    database = StringField()
    user = StringField()
    password = StringField()

    def __unicode__(self):
        return self.name

    def get_database(self):
        db = getattr(self, "_pmdb", None)
        if db:
            return db
        c = MongoClient(host=self.host, port=self.port)
        db = c[self.database]
        self._pmdb = db
        return db
