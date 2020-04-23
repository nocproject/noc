# ---------------------------------------------------------------------
# VRF, Prefix, IP state
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0043_default_resourcestates")]

    def migrate(self):
        # Create .state
        ResourceState = self.db.mock_model(
            model_name="ResourceState", db_table="main_resourcestate"
        )
        self.db.add_column(
            "ip_vrf",
            "state",
            models.ForeignKey(
                ResourceState, verbose_name="State", null=True, blank=True, on_delete=models.CASCADE
            ),
        )
        self.db.add_column(
            "ip_prefix",
            "state",
            models.ForeignKey(
                ResourceState, verbose_name="State", null=True, blank=True, on_delete=models.CASCADE
            ),
        )
        self.db.add_column(
            "ip_address",
            "state",
            models.ForeignKey(
                ResourceState, verbose_name="State", null=True, blank=True, on_delete=models.CASCADE
            ),
        )
