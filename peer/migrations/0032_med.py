# ----------------------------------------------------------------------
# med
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Adding field 'PeerGroup.local_pref'
        self.db.add_column(
            "peer_peergroup", "local_pref", models.IntegerField("Local Pref", null=True, blank=True)
        )
        # Adding field 'Peer.import_med'
        self.db.add_column(
            "peer_peer", "import_med", models.IntegerField("Local Pref", null=True, blank=True)
        )
        # Adding field 'PeerGroup.import_med'
        self.db.add_column(
            "peer_peergroup", "import_med", models.IntegerField("Local Pref", null=True, blank=True)
        )
        # Adding field 'Peer.export_med'
        self.db.add_column(
            "peer_peer", "export_med", models.IntegerField("Local Pref", null=True, blank=True)
        )
        # Adding field 'PeerGroup.export_med'
        self.db.add_column(
            "peer_peergroup", "export_med", models.IntegerField("Local Pref", null=True, blank=True)
        )
