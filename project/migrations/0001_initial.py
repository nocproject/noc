# ---------------------------------------------------------------------
# Project module models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.create_table(
            "project_project",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("code", models.CharField("Code", max_length=256, unique=True)),
                ("name", models.CharField("Name", max_length=256)),
                ("description", models.TextField("Description", null=True, blank=True)),
            ),
        )
