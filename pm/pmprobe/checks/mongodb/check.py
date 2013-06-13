## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MongoDBCheck
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from urllib import quote
## Contrib modules
import pymongo
import pymongo.errors
## NOC modules
from noc.pm.pmprobe.checks.base import BaseCheck, Counter, Gauge
from noc.sa.interfaces.base import StringParameter, IntParameter


class MongoDBCheck(BaseCheck):
    name = "mongodb"

    description = """
        MongoDB database monitoring
    """

    parameters = {
        "host": StringParameter(default="127.0.0.1"),
        "port": IntParameter(default=27017),
        "db": StringParameter(),
        "user": StringParameter(required=False),
        "password": StringParameter(required=False)
    }

    time_series = [
        Gauge("current_connections"),
        Gauge("available_connections"),
        Counter("created_connections"),
        Gauge("open_cursors"),
        Counter("documents_returned"),
        Counter("documents_inserted"),
        Counter("documents_deleted"),
        Counter("documents_updated"),
        Counter("network_in_octets"),
        Counter("network_out_octets"),
        Counter("network_requests"),
        Gauge("mem_resident"),
        Gauge("mem_virtual"),
        Gauge("mem_mapped")
    ]

    form = "NOC.pm.check.mongodb.MongoDBCheckForm"

    def apply_config(self):
        super(MongoDBCheck, self).apply_config()
        # Set up self.uri
        host = self.config.get("host")
        port = self.config.get("port")
        user = self.config.get("user")
        passwd = self.config.get("password")
        db = self.config.get("db")
        if user and passwd:
            self.uri = "mongodb://%s:%s@%s:%d/%s" % (
                quote(user), quote(passwd), host, port, db)
        else:
            self.uri = "mongodb://%s:%d/" % (host, port)

    def handle(self):
        try:
            client = pymongo.MongoClient(host=self.uri)
        except pymongo.errors.ConnectionFailure:
            self.error("Connection failed: %s" % self.uri)
            return None
        db = client[self.config["db"]]
        r = db.command("serverStatus")
        return {
            "current_connections": r["connections"]["current"],
            "available_connections": r["connections"]["available"],
            "created_connections": r["connections"]["totalCreated"],
            "open_cursors": r["cursors"]["totalOpen"],
            "documents_returned": r["metrics"]["document"]["returned"],
            "documents_inserted": r["metrics"]["document"]["inserted"],
            "documents_deleted": r["metrics"]["document"]["deleted"],
            "documents_updated": r["metrics"]["document"]["updated"],
            "network_in_octets": r["network"]["bytesIn"],
            "network_out_octets": r["network"]["bytesOut"],
            "network_requests": r["network"]["numRequests"],
            "mem_resident": r["mem"]["resident"],
            "mem_virtual": r["mem"]["virtual"],
            "mem_mapped": r["mem"]["mapped"]
        }
