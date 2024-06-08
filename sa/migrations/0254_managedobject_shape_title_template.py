# ----------------------------------------------------------------------
# ManagedObject, ManagedObjectProfile.shape_title_template
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # ManagedObjectProfile
        self.db.add_column(
            "sa_managedobjectprofile",
            "shape_title_template",
            models.CharField("Shape Title template", max_length=256, blank=True, null=True),
        )
        # ManagedObject
        self.db.add_column(
            "sa_managedobject",
            "shape_title_template",
            models.CharField("Shape Title template", max_length=256, blank=True, null=True),
        )
