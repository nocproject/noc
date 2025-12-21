# ----------------------------------------------------------------------
# Create ManagedObject watchers table
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class ObjectEffect(models.TextChoices):
    SUBSCRIPTION = "subscription", "Subscription"
    MAINTENANCE = "maintenance", "Maintenance"
    WF_EVENT = "wf_event", "WF Event"
    WIPING = "wiping", "Wiping"
    SUSPEND_JOB = "suspend_job", "Suspend Job"
    DIAGNOSTIC_CHECK = "diagnostic_check", "Diagnostic Check"


class Migration(BaseMigration):
    def migrate(self):
        ManagedObject = self.db.mock_model(model_name="ManagedObject", db_table="sa_managedobject")
        self.db.create_table(
            "sa_managedobjectwatchers",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "managed_object",
                    models.OneToOneField(
                        ManagedObject,
                        verbose_name="Managed Object Reference",
                        unique=False,
                        primary_key=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "effect",
                    models.CharField(
                        "Effect",
                        choices=ObjectEffect.choices,
                        max_length=20,
                        blank=False,
                        null=False,
                    ),
                ),
                ("key", models.CharField("Effect Key", max_length=64, null=True, blank=True)),
                ("once", models.BooleanField("Activate once", default=True)),
                ("wait_avail", models.BooleanField("Activate if Avail", default=False)),
                (
                    "after",
                    models.DateTimeField(
                        "Activate after time", auto_now_add=False, null=True, blank=True
                    ),
                ),
                (
                    "args",
                    models.JSONField("Activate once", null=True, blank=True, default=lambda: "{}"),
                ),
                ("remote_system", DocumentReferenceField("self", null=True, blank=True)),
            ),
        )
        self.db.create_index(
            "sa_managedobjectwatchers",
            [
                "managed_object_id",
                "effect",
                "key",
                "remote_system",
            ],
            unique=True,
        )
        # Migrate wiping ?
