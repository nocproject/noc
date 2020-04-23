# ---------------------------------------------------------------------
# Remove DNSZoneProfile.zone_ns_list, create necessary DNSServerObjects and links between zones and profiles
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):

        for p_id, zl in self.db.execute("SELECT id,zone_ns_list FROM dns_dnszoneprofile"):
            for n in [x.strip() for x in zl.split(",")]:
                if not self.db.execute("SELECT COUNT(*) FROM dns_dnsserver WHERE name=%s", [n])[0][
                    0
                ]:
                    self.db.execute("INSERT INTO dns_dnsserver(name) values (%s)", [n])
                self.db.execute(
                    """INSERT INTO dns_dnszoneprofile_ns_servers(dnszoneprofile_id,dnsserver_id)
                    SELECT %s,id
                    FROM dns_dnsserver
                    WHERE name=%s""",
                    [p_id, n],
                )

        self.db.delete_column("dns_dnszoneprofile", "zone_ns_list")
