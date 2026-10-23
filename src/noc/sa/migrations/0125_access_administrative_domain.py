# ----------------------------------------------------------------------
# administrativedomain access
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        AdministrativeDomain = self.db.mock_model(
            model_name="AdministrativeDomain", db_table="sa_administrativedomain"
        )
        for t in ("sa_useraccess", "sa_groupaccess"):
            self.db.add_column(
                t,
                "administrative_domain",
                models.ForeignKey(
                    AdministrativeDomain, null=True, blank=True, on_delete=models.CASCADE
                ),
            )
            self.db.execute(f"ALTER TABLE {t} ALTER selector_id DROP NOT NULL")
