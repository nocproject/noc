# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
##
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import uuid
import datetime
## Third-party modules
from south.db import db
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        now = datetime.datetime.now()
        sc = get_db()["noc.synccaches"]
        for zone_id, sync_id in db.execute(
            "SELECT z.id, s.sync "
            "FROM "
            "    dns_dnszone z JOIN dns_dnszoneprofile p ON (z.profile_id = p.id) "
            "    JOIN dns_dnszoneprofile_masters m ON (m.dnszoneprofile_id = p.id) "
            "    JOIN dns_dnsserver s ON (s.id = m.dnsserver_id) "
            "WHERE "
            "    z.is_auto_generated = TRUE "
            "    AND s.sync IS NOT NULL"
        ):
            if not sc.find({
                "model_id": "dns.DNSZone",
                "object_id": str(zone_id)
            }).count():
                sc.insert({
                    "uuid": str(uuid.uuid4()),
                    "model_id": "dns.DNSZone",
                    "object_id": str(zone_id),
                    "sync_id": str(sync_id),
                    "instance_id": 0,
                    "changed": now,
                    "expired": now
                })

    def backwards(self):
        pass
