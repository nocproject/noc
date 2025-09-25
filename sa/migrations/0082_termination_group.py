# ----------------------------------------------------------------------
# termination group
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
        # Model "TerminationGroup"
        self.db.create_table(
            "sa_terminationgroup",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64, unique=True)),
                ("description", models.TextField("Description", null=True, blank=True)),
            ),
        )
        TerminationGroup = self.db.mock_model(
            model_name="TerminationGroup", db_table="sa_terminationgroup"
        )
        # Alter sa_managedobject
        self.db.add_column(
            "sa_managedobject",
            "termination_group",
            models.ForeignKey(
                TerminationGroup,
                verbose_name="Termination Group",
                blank=True,
                null=True,
                related_name="termination_set",
                on_delete=models.CASCADE,
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "service_terminator",
            models.ForeignKey(
                TerminationGroup,
                verbose_name="Service Terminator",
                blank=True,
                null=True,
                related_name="access_set",
                on_delete=models.CASCADE,
            ),
        )
        # Selector
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_termination_group",
            models.ForeignKey(
                TerminationGroup,
                verbose_name="Filter by termination group",
                null=True,
                blank=True,
                related_name="selector_termination_group_set",
                on_delete=models.CASCADE,
            ),
        )
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_service_terminator",
            models.ForeignKey(
                TerminationGroup,
                verbose_name="Filter by service terminator",
                null=True,
                blank=True,
                related_name="selector_service_terminator_set",
                on_delete=models.CASCADE,
            ),
        )
