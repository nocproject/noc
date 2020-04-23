# ----------------------------------------------------------------------
# event correlation rule
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
        # Model 'EventCorrelationRule'
        self.db.create_table(
            "fm_eventcorrelationrule",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64, unique=True)),
                ("rule", models.TextField("Rule")),
                ("description", models.TextField("Description", null=True, blank=True)),
                ("is_builtin", models.BooleanField("Is Builtin", default=False)),
            ),
        )
