# ----------------------------------------------------------------------
# inet rtr
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
        AS = self.db.mock_model(model_name="AS", db_table="peer_as")
        if self.db.execute("SELECT COUNT(*) FROM peer_peeringpoint")[0][0] > 0:
            self.db.add_column(
                "peer_peeringpoint",
                "local_as",
                models.ForeignKey(AS, verbose_name="Local AS", blank=True, null=True),
            )
            as_id = self.db.execute("SELECT MIN(id) FROM peer_as")[0][0]
            self.db.execute("UPDATE peer_peeringpoint SET local_as_id=%s", [as_id])
            self.db.execute("ALTER TABLE peer_peeringpoint ALTER local_as_id SET NOT NULL")
        else:
            self.db.add_column(
                "peer_peeringpoint",
                "local_as",
                models.ForeignKey(AS, verbose_name="Local AS", on_delete=models.CASCADE),
            )
        self.db.add_column(
            "peer_peer", "masklen", models.PositiveIntegerField("Masklen", default=30)
        )
