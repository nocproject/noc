# ----------------------------------------------------------------------
# AdministrativeDomain.biosegmentation_*
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        Template = self.db.mock_model(model_name="Template", db_table="main_template")
        self.db.add_column(
            "sa_administrativedomain",
            "bioseg_floating_name_template",
            models.ForeignKey(Template, null=True, blank=True, on_delete=models.CASCADE),
        )
        self.db.add_column(
            "sa_administrativedomain",
            "bioseg_floating_parent_segment",
            DocumentReferenceField("inv.NetworkSegment", null=True, blank=True),
        )
