# ---------------------------------------------------------------------
# Create sa_objectnotification table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Mock Models
        ManagedObjectSelector = self.db.mock_model(
            model_name="ManagedObjectSelector", db_table="sa_managedobjectselector"
        )
        NotificationGroup = self.db.mock_model(
            model_name="NotificationGroup", db_table="main_notificationgroup"
        )
        # Model "Activator"
        self.db.create_table(
            "sa_objectnotification",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("selector", models.ForeignKey(ManagedObjectSelector, on_delete=models.CASCADE)),
                (
                    "notification_group",
                    models.ForeignKey(NotificationGroup, on_delete=models.CASCADE),
                ),
                # Events
                ("config_changed", models.BooleanField("Config changed")),
                ("alarm_risen", models.BooleanField("Alarm risen")),
                ("alarm_cleared", models.BooleanField("Alarm cleared")),
                ("alarm_commented", models.BooleanField("Alarm commented")),
                ("new", models.BooleanField("New")),
                ("deleted", models.BooleanField("Deleted")),
                ("version_changed", models.BooleanField("Version changed")),
                ("interface_changed", models.BooleanField("Interface changed")),
                ("script_failed", models.BooleanField("Script failed")),
                ("config_policy_violation", models.BooleanField("Config policy violation")),
            ),
        )
