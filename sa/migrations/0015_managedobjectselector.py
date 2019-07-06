# ----------------------------------------------------------------------
# managedobjectselector
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
        # Mock Models
        AdministrativeDomain = self.db.mock_model(
            model_name="AdministrativeDomain", db_table="sa_administrativedomain"
        )

        # Model 'ManagedObjectSelector'
        self.db.create_table(
            "sa_managedobjectselector",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64, unique=True)),
                ("description", models.TextField("Description", blank=True, null=True)),
                ("is_enabled", models.BooleanField("Is Enabled", default=True)),
                ("filter_id", models.IntegerField("Filter by ID", null=True, blank=True)),
                (
                    "filter_name",
                    models.CharField(
                        "Filter by Name (REGEXP)", max_length=256, null=True, blank=True
                    ),
                ),
                (
                    "filter_profile",
                    models.CharField("Filter by Profile", max_length=64, null=True, blank=True),
                ),
                (
                    "filter_address",
                    models.CharField(
                        "Filter by Address (REGEXP)", max_length=256, null=True, blank=True
                    ),
                ),
                (
                    "filter_administrative_domain",
                    models.ForeignKey(
                        AdministrativeDomain,
                        verbose_name="Filter by Administrative Domain",
                        null=True,
                        blank=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "filter_user",
                    models.CharField(
                        "Filter by User (REGEXP)", max_length=256, null=True, blank=True
                    ),
                ),
                (
                    "filter_remote_path",
                    models.CharField(
                        "Filter by Remote Path (REGEXP)", max_length=256, null=True, blank=True
                    ),
                ),
                (
                    "filter_description",
                    models.CharField(
                        "Filter by Description (REGEXP)", max_length=256, null=True, blank=True
                    ),
                ),
                (
                    "filter_repo_path",
                    models.CharField(
                        "Filter by Repo Path (REGEXP)", max_length=256, null=True, blank=True
                    ),
                ),
                (
                    "source_combine_method",
                    models.CharField(
                        "Source Combine Method",
                        max_length=1,
                        default="O",
                        choices=[("A", "AND"), ("O", "OR")],
                    ),
                ),
            ),
        )
        # Mock Models
        ManagedObjectSelector = self.db.mock_model(
            model_name="ManagedObjectSelector", db_table="sa_managedobjectselector"
        )
        ObjectGroup = self.db.mock_model(model_name="ObjectGroup", db_table="sa_objectgroup")

        # M2M field 'ManagedObjectSelector.filter_groups'
        self.db.create_table(
            "sa_managedobjectselector_filter_groups",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "managedobjectselector",
                    models.ForeignKey(ManagedObjectSelector, null=False, on_delete=models.CASCADE),
                ),
                (
                    "objectgroup",
                    models.ForeignKey(ObjectGroup, null=False, on_delete=models.CASCADE),
                ),
            ),
        )
        # Mock Models
        ManagedObjectSelector = self.db.mock_model(
            model_name="ManagedObjectSelector", db_table="sa_managedobjectselector"
        )
        self.db.create_table(
            "sa_managedobjectselector_sources",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "from_managedobjectselector",
                    models.ForeignKey(ManagedObjectSelector, null=False, on_delete=models.CASCADE),
                ),
                (
                    "to_managedobjectselector",
                    models.ForeignKey(ManagedObjectSelector, null=False, on_delete=models.CASCADE),
                ),
            ),
        )
