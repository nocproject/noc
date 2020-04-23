# ----------------------------------------------------------------------
# managedobjectselector filter_object_profile
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
        ManagedObjectProfile = self.db.mock_model(
            model_name="ManagedObjectProfile", db_table="sa_managedobjectprofile"
        )
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_object_profile",
            models.ForeignKey(
                ManagedObjectProfile,
                verbose_name="Filter by Object Profile",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        )
