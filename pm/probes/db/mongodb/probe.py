## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MongoDB probes
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
try:
    import pymongo
    import pymongo.errors
except ImportError:
    pymongo = None
## NOC modules
from noc.pm.probes.base import Probe, metric


class MongoDBProbe(Probe):
    TITLE = "MongoDB"
    DESCRIPTION = "MongoDB server statistics"
    TAGS = ["db", "mongodb"]
    CONFIG_FORM = "MongoDBConfig"

    @metric([
        "DB | Ops | Query", "DB | Ops | Command",
        "DB | Ops | Insert", "DB | Ops | Update", "DB | Ops | Delete",
        "DB | Network | Requests",
        "DB | Connections | Rate",
        "MongoDB | TTL | Deleted",
        "DB | Index | Access", "DB | Index | Hits", "DB | Index | Misses",
        "Process | Memory | Page Faults",
        "DB | Transaction | Commit"
    ], convert=metric.DERIVE, preference=metric.PREF_PLATFORM)
    @metric([
        "DB | Network | In", "DB | Network | Out"
    ], convert=metric.DERIVE, preference=metric.PREF_PLATFORM, scale=8)
    @metric([
        "DB | Connections | Current", "DB | Connections | Available",
        "Process | Memory | Resident", "Process | Memory | Virtual",
        "Process | Memory | Mapped"
    ], convert=metric.NONE, preference=metric.PREF_PLATFORM)
    def get_server_stats(self, host, database, port=27017):
        if not pymongo:
            self.logger.error("pymongo is not installed. Disabling probe")
            self.disable()
            return
        try:
            mc = pymongo.MongoClient(host=host, port=int(port))
        except pymongo.errors.ConnectionFailure, why:
            self.logger.error("Connection failure: %s", why)
            return None
        db = mc[database]
        ss = db.command("serverStatus")
        return {
            "DB | Ops | Query": ss["opcounters"]["query"],
            "DB | Ops | Command": ss["opcounters"]["command"],
            "DB | Ops | Insert": ss["opcounters"]["insert"],
            "DB | Ops | Update": ss["opcounters"]["update"],
            "DB | Ops | Delete": ss["opcounters"]["delete"],
            "DB | Network | Requests": ss["network"]["numRequests"],
            "DB | Network | In": ss["network"]["bytesIn"],
            "DB | Network | Out": ss["network"]["bytesOut"],
            "DB | Connections | Current": ss["connections"]["current"],
            "DB | Connections | Available": ss["connections"]["available"],
            "DB | Connections | Rate": ss["connections"].get("totalCreated", 0),
            "Process | Memory | Resident": ss["mem"]["resident"],
            "Process | Memory | Virtual": ss["mem"]["virtual"],
            "Process | Memory | Mapped": ss["mem"]["mapped"],
            "Process | Memory | Page Faults": ss.get("extra_info", {}).get("page_faults", 0),
            "MongoDB | TTL | Deleted": ss["metrics"].get("ttl", {}).get("deletedDocuments", 0),
            "DB | Index | Access": ss["indexCounters"]["accesses"],
            "DB | Index | Hits": ss["indexCounters"]["hits"],
            "DB | Index | Misses": ss["indexCounters"]["misses"],
            "DB | Transaction | Commit": ss["dur"]["commits"]
        }
