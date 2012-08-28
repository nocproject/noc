# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Persistent storage for STOMP daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import time
## NOC modules
from noc.lib.nosql import get_db

class Storage(object):
    def __init__(self):
        self.collection = get_db().noc.stomp.persistent
        self.collection.ensure_index("ts")
        self.collection.ensure_index("dest")

    def debug(self, msg):
        logging.debug("[Storage] %s" % msg)

    def debug(self, msg):
        logging.info("[Storage] %s" % msg)

    def put(self, destination, headers, body):
        self.collection.insert({
            "dest": destination,
            "headers": headers,
            "body": body,
            "ts": time.time()
        }, safe=True)

    def get_messages(self, destination):
        for d in self.collection.find({
            "dest": destination}).sort("ts"):
            yield d["_id"], d["headers"], d["body"]

    def remove(self, id):
        self.collection.remove({"_id": id})
