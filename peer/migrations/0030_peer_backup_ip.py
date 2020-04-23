# ----------------------------------------------------------------------
# peer backup ip
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.model.fields import INETField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Adding field 'Peer.remote_backup_ip'
        self.db.add_column(
            "peer_peer", "remote_backup_ip", INETField("Remote Backup IP", null=True, blank=True)
        )
        # Adding field 'Peer.local_backup_ip'
        self.db.add_column(
            "peer_peer", "local_backup_ip", INETField("Local Backup IP", null=True, blank=True)
        )
