# ----------------------------------------------------------------------
# Migrate ManagedObjectSelect filter labels
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from django.contrib.postgres.fields import ArrayField
from django.db.models import CharField


class Migration(BaseMigration):
    depends_on = [("sa", "0213_labels")]

    def migrate(self):
        # Create labels fields
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_labels",
            ArrayField(CharField(max_length=250), null=True, blank=True, default=lambda: "{}"),
        )
        self.db.execute(
            """
            UPDATE sa_managedobjectselector
            SET filter_labels = filter_tags
            WHERE filter_tags is not NULL and filter_tags <> '{}'
            """
        )
        self.db.delete_column(
            "sa_managedobjectselector",
            "filter_tags",
        )
        self.db.execute(
            'CREATE INDEX x_sa_managedobjectselector_labels ON "sa_managedobjectselector" USING GIN("filter_labels")'
        )
