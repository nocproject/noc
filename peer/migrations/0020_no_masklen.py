# ----------------------------------------------------------------------
# no masklen
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        for peer_id, local_ip, remote_ip, masklen in self.db.execute(
            "SELECT id,local_ip,remote_ip,masklen FROM peer_peer"
        ):
            if "/" not in local_ip:
                local_ip += "/%d" % masklen
            if "/" not in remote_ip:
                remote_ip += "/%d" % masklen
            self.db.execute(
                "UPDATE peer_peer SET local_ip=%s,remote_ip=%s WHERE id=%s",
                [local_ip, remote_ip, peer_id],
            )
        self.db.execute("COMMIT")
        self.db.delete_column("peer_peer", "masklen")
