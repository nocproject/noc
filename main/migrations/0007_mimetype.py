# ----------------------------------------------------------------------
# mimetype
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
        # Model 'MIMEType'
        self.db.create_table(
            "main_mimetype",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("extension", models.CharField("Extension", max_length=32, unique=True)),
                ("mime_type", models.CharField("MIME Type", max_length=63)),
            ),
        )
