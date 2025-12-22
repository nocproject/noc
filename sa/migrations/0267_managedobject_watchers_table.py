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
                ("id", models.AutoField(verbose_name="ID", primary_key=False, auto_created=True)),
                (
                    "managed_object",
                    models.ForeignKey(
                        ManagedObject, verbose_name="Managed Object", on_delete=models.CASCADE
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
                (
                    "key",
                    models.CharField(
                        "Effect Key", max_length=64, null=False, blank=True, default=""
                    ),
                ),
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
                # Before Postgres 15 nulls not equals. It and unique constraints not worked for NULL value
                (
                    "remote_system",
                    models.CharField(
                        "Remote System", max_length=24, null=False, blank=True, default=""
                    ),
                ),
            ),
        )
        self.db.execute(
            """ALTER TABLE sa_managedobjectwatchers
             ADD CONSTRAINT sa_managedobjectwatchers_uniques
             UNIQUE (managed_object_id,effect,key,remote_system)
             """
        )
        self.db.add_column(
            "sa_managedobject",
            "watcher_wait_ts",
            models.DateTimeField("Last Seen", blank=True, null=True),
        )
        self.db.create_index("sa_managedobject", ["watcher_wait_ts"], unique=False)
