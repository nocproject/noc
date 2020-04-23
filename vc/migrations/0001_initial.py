# ---------------------------------------------------------------------
# Initial migration for VC application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Model 'VCDomain'
        self.db.create_table(
            "vc_vcdomain",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64, unique=True)),
                ("description", models.TextField("Description", blank=True, null=True)),
            ),
        )

        # Mock Models
        VCDomain = self.db.mock_model(model_name="VCDomain", db_table="vc_vcdomain")

        # Model 'VC'
        self.db.create_table(
            "vc_vc",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "vc_domain",
                    models.ForeignKey(VCDomain, verbose_name="VC Domain", on_delete=models.CASCADE),
                ),
                ("type", models.CharField("Type", max_length=1)),
                ("l1", models.IntegerField("Label 1")),
                ("l2", models.IntegerField("Label 2", default=0)),
                ("description", models.CharField("Description", max_length=256)),
            ),
        )
        self.db.create_index("vc_vc", ["vc_domain_id", "type", "l1", "l2"], unique=True)
