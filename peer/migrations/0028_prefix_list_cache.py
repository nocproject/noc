# ----------------------------------------------------------------------
# prefix list cache
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.fields import InetArrayField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Adding model 'PrefixListCache'
        PeeringPoint = self.db.mock_model(model_name="PeeringPoint", db_table="peer_peeringpoint")
        self.db.create_table(
            "peer_prefixlistcache",
            (
                ("id", models.AutoField(primary_key=True)),
                (
                    "peering_point",
                    models.ForeignKey(
                        PeeringPoint, verbose_name="Peering Point", on_delete=models.CASCADE
                    ),
                ),
                ("name", models.CharField("Name", max_length=64)),
                ("data", InetArrayField("Data")),
                ("strict", models.BooleanField("Strict")),
                ("changed", models.DateTimeField("Changed", auto_now=True, auto_now_add=True)),
                ("pushed", models.DateTimeField("Pushed", null=True, blank=True)),
            ),
        )
