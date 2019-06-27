# ----------------------------------------------------------------------
# command snippet
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import AutoCompleteTagsField


class Migration(BaseMigration):
    def migrate(self):
        # Mock models
        ManagedObjectSelector = self.db.mock_model(
            model_name="ManagedObjectSelector",
            db_table="sa_managedobjectselector"
        )

        # Model "ReduceTask"
        self.db.create_table(
            "sa_commandsnippet", (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=128, unique=True)),
                ("description", models.TextField("Description")),
                ("snippet", models.TextField("Snippet")),
                ("change_configuration", models.BooleanField("Change configuration", default=False)),
                ("selector", models.ForeignKey(ManagedObjectSelector, verbose_name="Object Selector", on_delete=models.CASCADE)),
                ("is_enabled", models.BooleanField("Is Enabled?", default=True)),
                ("timeout", models.IntegerField("Timeout", default=60)),
                ("tags", AutoCompleteTagsField("Tags", null=True, blank=True)),
            )
        )
