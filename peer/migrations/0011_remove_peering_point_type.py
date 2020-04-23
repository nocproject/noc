# ----------------------------------------------------------------------
# remove peering point type
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party models
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "peer_peeringpoint",
            "profile_name",
            models.CharField("Profile", max_length=128, null=True),
        )
        self.db.add_column(
            "peer_lgquerycommand",
            "profile_name",
            models.CharField("Profile", max_length=128, null=True),
        )

        for id, n in self.db.execute("SELECT id,name FROM peer_peeringpointtype"):
            self.db.execute(
                "UPDATE peer_peeringpoint SET profile_name=%s WHERE type_id=%s", [n, id]
            )
            self.db.execute(
                "UPDATE peer_lgquerycommand SET profile_name=%s WHERE peering_point_type_id=%s",
                [n, id],
            )
        self.db.delete_column("peer_peeringpoint", "type_id")
        self.db.delete_column("peer_lgquerycommand", "peering_point_type_id")
        self.db.delete_table("peer_peeringpointtype")
        self.db.execute("ALTER TABLE peer_peeringpoint ALTER profile_name SET NOT NULL")
        self.db.execute("ALTER TABLE peer_lgquerycommand ALTER profile_name SET NOT NULL")
