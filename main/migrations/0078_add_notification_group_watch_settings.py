# ----------------------------------------------------------------------
# Add Notification Group Settings to User
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
from django.contrib.postgres.fields import ArrayField

# NOC modules
from noc.core.model.fields import DocumentReferenceField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):

    def migrate(self):
        self.db.delete_column("main_notificationgroupusersubscription", "watch")
        self.db.delete_column("main_notificationgroupusersubscription", "remote_system")
        # Model 'NotificationGroupUser'
        NotificationGroup = self.db.mock_model(
            model_name="NotificationGroup", db_table="main_notificationgroup"
        )
        self.db.create_table(
            "main_notificationgroupwatchsubscription",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "notification_group",
                    models.ForeignKey(
                        NotificationGroup,
                        verbose_name="Notification Group",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("model_id", models.CharField("Name", max_length=50)),
                ("instance_id", models.CharField("Name", max_length=100)),
                (
                    "watchers",
                    ArrayField(
                        models.CharField(max_length=100),
                        null=True,
                        blank=True,
                        default=lambda: "{}",
                    ),
                ),
                (
                    "suppresses",
                    ArrayField(
                        models.CharField(max_length=100),
                        null=True,
                        blank=True,
                        default=lambda: "{}",
                    ),
                ),
                ("remote_system", DocumentReferenceField("self", null=True, blank=True)),
            ),
        )
        self.db.create_index(
            "main_notificationgroupwatchsubscription",
            [
                "notification_group_id",
                "model_id",
                "instance_id",
                "remote_system",
            ],
            unique=True,
        )
