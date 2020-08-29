# ----------------------------------------------------------------------
# project integration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        # Project
        self.db.add_column(
            "project_project",
            "remote_system",
            DocumentReferenceField("self", null=True, blank=True),
        )
        self.db.add_column(
            "project_project", "remote_id", models.CharField(max_length=64, null=True, blank=True),
        )
        self.db.add_column(
            "project_project", "bi_id", models.BigIntegerField(null=True, blank=True)
        )
