# ----------------------------------------------------------------------
# Migrate ObjectData
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.contrib.postgres.fields import ArrayField
from django.db.models import IntegerField

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import ObjectIDArrayField


class Migration(BaseMigration):

    def migrate(self):
        # Create uplinks fields
        self.db.add_column(
            "sa_managedobject",
            "uplinks",
            ArrayField(IntegerField(), db_index=True, null=True, blank=True, default=lambda: "{}"),
        )
        self.db.add_column(
            "sa_managedobject",
            "rca_neighbors",
            ArrayField(IntegerField(), null=True, blank=True, default=lambda: "{}"),
        )
        self.db.add_column(
            "sa_managedobject",
            "dlm_windows",
            ArrayField(IntegerField(), null=True, blank=True, default=lambda: "{}"),
        )
        # Path cache fields
        self.db.add_column(
            "sa_managedobject",
            "adm_path",
            ArrayField(IntegerField(), null=True, blank=True, default=lambda: "{}"),
        )
        self.db.add_column(
            "sa_managedobject",
            "segment_path",
            ObjectIDArrayField(db_index=True, default="{}"),
        )
        self.db.add_column(
            "sa_managedobject",
            "container_path",
            ObjectIDArrayField(db_index=True, default="{}"),
        )
