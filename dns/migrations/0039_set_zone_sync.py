# ---------------------------------------------------------------------
# set zone sync
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import uuid
import datetime

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        now = datetime.datetime.now()
        sc = self.mongo_db["noc.synccaches"]
        for zone_id, sync_id in self.db.execute(
            """SELECT z.id, s.sync
                 FROM
                     dns_dnszone z JOIN dns_dnszoneprofile p ON (z.profile_id = p.id)
                     JOIN dns_dnszoneprofile_masters m ON (m.dnszoneprofile_id = p.id)
                     JOIN dns_dnsserver s ON (s.id = m.dnsserver_id)
                 WHERE
                     z.is_auto_generated = TRUE
                     AND s.sync IS NOT NULL"""
        ):
            if not sc.count_documents(
                {"sync_id": str(sync_id), "model_id": "dns.DNSZone", "object_id": str(zone_id)}
            ):
                sc.insert_one(
                    {
                        "uuid": str(uuid.uuid4()),
                        "model_id": "dns.DNSZone",
                        "object_id": str(zone_id),
                        "sync_id": str(sync_id),
                        "instance_id": 0,
                        "changed": now,
                        "expire": now,
                    }
                )
