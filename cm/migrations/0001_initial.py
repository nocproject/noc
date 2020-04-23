# ----------------------------------------------------------------------
# initial
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

        # Model 'ObjectCategory'
        self.db.create_table(
            "cm_objectcategory",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64, unique=True)),
                (
                    "description",
                    models.CharField("Description", max_length=128, null=True, blank=True),
                ),
            ),
        )
        # Model 'Object'
        self.db.create_table(
            "cm_object",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("handler_class_name", models.CharField("Object Type", max_length=64)),
                ("stream_url", models.CharField("URL", max_length=128)),
                ("profile_name", models.CharField("Profile", max_length=128)),
                ("repo_path", models.CharField("Repo Path", max_length=128)),
                (
                    "push_every",
                    models.PositiveIntegerField(
                        "Push Every (secs)", default=86400, blank=True, null=True
                    ),
                ),
                ("next_push", models.DateTimeField("Next Push", blank=True, null=True)),
                ("last_push", models.DateTimeField("Last Push", blank=True, null=True)),
                (
                    "pull_every",
                    models.PositiveIntegerField(
                        "Pull Every (secs)", default=86400, blank=True, null=True
                    ),
                ),
                ("next_pull", models.DateTimeField("Next Pull", blank=True, null=True)),
                ("last_pull", models.DateTimeField("Last Pull", blank=True, null=True)),
            ),
        )
        # Mock Models
        Object = self.db.mock_model(model_name="Object", db_table="cm_object")
        ObjectCategory = self.db.mock_model(
            model_name="ObjectCategory", db_table="cm_objectcategory"
        )

        # M2M field 'Object.categories'
        self.db.create_table(
            "cm_object_categories",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("object", models.ForeignKey(Object, null=False, on_delete=models.CASCADE)),
                (
                    "objectcategory",
                    models.ForeignKey(ObjectCategory, null=False, on_delete=models.CASCADE),
                ),
            ),
        )
        self.db.create_index("cm_object", ["handler_class_name", "repo_path"], unique=True)
