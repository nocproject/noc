# ----------------------------------------------------------------------
# Project.shape_overlay_*
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
        self.db.add_column(
            "project_project",
            "shape_overlay_glyph",
            DocumentReferenceField("main.Glyph", null=True, blank=True),
        )
        self.db.add_column(
            "project_project",
            "shape_overlay_position",
            models.CharField("S.O. Position", max_length=2, null=True, blank=True,),
        )
        self.db.add_column(
            "project_project",
            "shape_overlay_form",
            models.CharField("S.O. Form", max_length=1, null=True, blank=True,),
        )
