# ---------------------------------------------------------------------
# asset project
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("project", "0001_initial")]

    def migrate(self):
        # Create .project
        Project = self.db.mock_model(model_name="Project", db_table="project_project")
        for t in ["peer_asset"]:
            self.db.add_column(
                t,
                "project",
                models.ForeignKey(
                    Project, verbose_name="Project", null=True, blank=True, on_delete=models.CASCADE
                ),
            )
