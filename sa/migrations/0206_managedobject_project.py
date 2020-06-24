# ----------------------------------------------------------------------
# ManagedObject.project
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        Project = self.db.mock_model(model_name="Project", db_table="project_project")
        self.db.add_column(
            "sa_managedobject",
            "project",
            models.ForeignKey(Project, null=True, blank=True, on_delete=models.CASCADE),
        )
