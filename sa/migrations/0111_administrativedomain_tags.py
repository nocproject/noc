# ----------------------------------------------------------------------
# administrativedomain tags
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import TagsField


class Migration(BaseMigration):
    def migrate(self):
        AdministrativeDomain = self.db.mock_model(
            model_name="AdministrativeDomain", db_table="sa_administrativedomain"
        )
        self.db.add_column(
            "sa_administrativedomain", "tags", TagsField("Tags", null=True, blank=True)
        )
        self.db.add_column(
            "sa_administrativedomain",
            "parent",
            models.ForeignKey(
                AdministrativeDomain,
                verbose_name="Parent",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        )
