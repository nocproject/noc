# ----------------------------------------------------------------------
# pyrule
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
        # Adding model 'PyRule'
        self.db.create_table(
            "main_pyrule",
            (
                ("id", models.AutoField(primary_key=True)),
                ("name", models.CharField("Name", unique=True, max_length=64)),
                ("interface", models.CharField("Interface", max_length=64)),
                ("description", models.TextField("Description")),
                ("text", models.TextField("Text")),
                ("changed", models.DateTimeField("Changed", auto_now=True, auto_now_add=True)),
            ),
        )
