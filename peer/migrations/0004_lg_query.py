# ----------------------------------------------------------------------
# lg query
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
        # Model 'LGQueryType'
        self.db.create_table(
            "peer_lgquerytype",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=32, unique=True)),
            ),
        )

        # Mock Models
        PeeringPointType = self.db.mock_model(
            model_name="PeeringPointType", db_table="peer_peeringpointtype"
        )
        LGQueryType = self.db.mock_model(model_name="LGQueryType", db_table="peer_lgquerytype")

        # Model 'LGQueryCommand'
        self.db.create_table(
            "peer_lgquerycommand",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "peering_point_type",
                    models.ForeignKey(
                        PeeringPointType,
                        verbose_name="Peering Point Type",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "query_type",
                    models.ForeignKey(
                        LGQueryType, verbose_name="LG Query Type", on_delete=models.CASCADE
                    ),
                ),
                ("command", models.CharField("Command", max_length=128)),
            ),
        )
        self.db.create_index(
            "peer_lgquerycommand", ["peering_point_type_id", "query_type_id"], unique=True
        )
