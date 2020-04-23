# ----------------------------------------------------------------------
# default vrf
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("peer", "0017_default_maintainer")]

    def migrate(self):
        if self.db.execute("SELECT COUNT(*) FROM ip_vrfgroup")[0][0] == 0:
            self.db.execute("INSERT INTO ip_vrfgroup(name) VALUES(%s)", ["default"])
        if self.db.execute("SELECT COUNT(*) FROM peer_as WHERE asn=%s", [0])[0][0] == 0:
            maintainer_id = self.db.execute("SELECT id FROM peer_maintainer LIMIT 1")[0][0]
            self.db.execute(
                "INSERT INTO peer_as(asn,description,maintainer_id) VALUES(%s,%s,%s)",
                [0, "Default", maintainer_id],
            )
        if self.db.execute("SELECT COUNT(*) FROM ip_vrf")[0][0] == 0:
            vg_id = self.db.execute("SELECT id FROM ip_vrfgroup LIMIT 1")[0][0]
            self.db.execute(
                "INSERT INTO ip_vrf(name,vrf_group_id,rd) VALUES(%s,%s,%s)",
                ["default", vg_id, "0:0"],
            )
            vrf_id = self.db.execute("SELECT id FROM ip_vrf LIMIT 1")[0][0]
            user_id = self.db.execute("SELECT id FROM auth_user LIMIT 1")[0][0]
            asn_id = self.db.execute("SELECT id FROM peer_as WHERE asn=%s", [0])[0][0]
            self.db.execute(
                """INSERT INTO ip_ipv4block(prefix,description,vrf_id,asn_id,modified_by_id,last_modified)
                VALUES(%s,%s,%s,%s,%s,%s)""",
                ["0.0.0.0/0", "Root", vrf_id, asn_id, user_id, "now"],
            )

    def backwards(self):
        pass
