# ----------------------------------------------------------------------
# managedobjectprofile bgppeer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("peer", "0046_migrate_peer_for_discovery")]

    def migrate(self):
        # Box
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_bgppeer",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "bgpeer_discovery_policy",
            models.CharField(
                "BGP Peer Discovery Policy",
                max_length=1,
                choices=[
                    ("s", "Script"),
                    ("S", "Script, ConfDB"),
                    ("C", "ConfDB, Script"),
                    ("c", "ConfDB"),
                ],
                default="c",
            ),
        )
        PeerProfile = self.db.mock_model(model_name="PeerProfile", db_table="peer_peer")
        self.db.add_column(
            "sa_managedobjectprofile",
            "bgppeer_profile",
            models.ForeignKey(
                PeerProfile,
                verbose_name="PeerProfile",
                blank=True,
                null=True,
                on_delete=models.CASCADE,
            ),
        )
        # Peer Status
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_periodic_discovery_peerstatus",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_peerstatus_interval",
            models.IntegerField(default=0),
        )
