# ----------------------------------------------------------------------
# ManagedObjectProfile db_table Fix bgppeer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("sa", "0261_managedobjectprofile_add_discovery_bgpeer")]

    def migrate(self):
        self.db.delete_column("sa_managedobjectprofile", "bgppeer_profile_id")
        PeerProfile = self.db.mock_model(model_name="PeerProfile", db_table="peer_peerprofile")
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
