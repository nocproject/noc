# ----------------------------------------------------------------------
# ManagedObjectProfile config download settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        Template = self.db.mock_model(model_name="Template", db_table="main_template")
        self.db.add_column(
            "sa_managedobjectprofile",
            "config_download_storage",
            DocumentReferenceField("main.ExtStorage", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "config_download_template",
            models.ForeignKey(
                Template,
                verbose_name="Config download Template",
                blank=True,
                null=True,
                on_delete=models.CASCADE,
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "config_policy",
            models.CharField(
                "Config download Policy",
                max_length=1,
                choices=[
                    ("s", "Script"),
                    ("S", "Script, Download"),
                    ("D", "Download, Script"),
                    ("d", "Download"),
                ],
                default="s",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "config_policy",
            models.CharField(
                "Config download Policy",
                max_length=1,
                choices=[
                    ("P", "Profile"),
                    ("s", "Script"),
                    ("S", "Script, Download"),
                    ("D", "Download, Script"),
                    ("d", "Download"),
                ],
                default="P",
            ),
        )
