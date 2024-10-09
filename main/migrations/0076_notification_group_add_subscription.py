# ----------------------------------------------------------------------
# Add message_type to Template models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import uuid
from collections import defaultdict

# Third-party modules
import orjson
from django.db import models
from django.contrib.postgres.fields import ArrayField

# NOC modules
from noc.core.model.fields import DocumentReferenceField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):

    def create_subscription(self):
        # Mock Models
        NotificationGroup = self.db.mock_model(
            model_name="NotificationGroup", db_table="main_notificationgroup"
        )
        TimePattern = self.db.mock_model(model_name="TimePattern", db_table="main_timepattern")
        User = self.db.mock_model(model_name="User", db_table="auth_user")

        # Model 'NotificationGroupUser'
        self.db.create_table(
            "main_notificationgroupusersubscription",
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
                (
                    "time_pattern",
                    models.ForeignKey(
                        TimePattern,
                        verbose_name="Time Pattern",
                        on_delete=models.CASCADE,
                        null=True,
                        blank=True,
                    ),
                ),
                ("user", models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)),
                (
                    "expired_at",
                    models.DateTimeField("Expired Subscription After", null=True, blank=True),
                ),
                ("suppress", models.BooleanField("Deactivate Subscription", default=False)),
                (
                    "watch",
                    models.CharField("Watch key", max_length=100, null=True, blank=True),
                ),
                ("remote_system", DocumentReferenceField("self", null=True, blank=True)),
            ),
        )
        self.db.create_index(
            "main_notificationgroupusersubscription",
            [
                "notification_group_id",
                "user_id",
                "watch",
            ],
            unique=True,
        )

    def migrate(self):
        self.create_subscription()
        self.db.add_column("main_notificationgroup", "uuid", models.UUIDField(null=True))
        for id in self.db.execute("SELECT id FROM main_notificationgroup"):
            u = str(uuid.uuid4())
            self.db.execute(
                "UPDATE main_notificationgroup SET uuid=%s WHERE id =%s and uuid IS NULL", [u, id]
            )
        self.db.add_column(
            "main_notificationgroup",
            "message_register_policy",
            models.CharField("Name", max_length=1, default="d"),
        )
        self.db.add_column(
            "main_notificationgroup",
            "message_types",
            models.JSONField("Notification Contacts", null=True, blank=True, default=lambda: "[]"),
        )
        self.db.add_column(
            "main_notificationgroup",
            "static_members",
            models.JSONField("Notification Contacts", null=True, blank=True, default=lambda: "[]"),
        )
        self.db.add_column(
            "main_notificationgroup",
            "subscription_settings",
            models.JSONField(
                "Notification Subscriptions", null=True, blank=True, default=lambda: "[]"
            ),
        )
        self.db.add_column(
            "main_notificationgroup",
            "subscription_to",
            ArrayField(
                models.CharField(max_length=100), null=True, blank=True, default=lambda: "{}"
            ),
        )
        self.db.add_column(
            "main_notificationgroup",
            "conditions",
            models.JSONField(
                "Condition for match Notification Group",
                null=True,
                blank=True,
                default=lambda: "[]",
            ),
        )
        r = defaultdict(list)
        for ng, tp, method, contact in self.db.execute(
            "SELECT notification_group_id, time_pattern_id, notification_method, params FROM main_notificationgroupother"
        ):
            r[ng].append(
                {
                    "contact": contact,
                    "notification_method": method,
                    "time_patter": tp or None,
                }
            )
        for ng, members in r.items():
            self.db.execute(
                """UPDATE main_notificationgroup SET static_members = %s::jsonb WHERE id = %s""",
                [orjson.dumps(members).decode(), ng],
            )
        for ng, tp, user in self.db.execute(
            "SELECT notification_group_id, time_pattern_id, user_id FROM main_notificationgroupuser"
        ):
            self.db.execute(
                "INSERT INTO main_notificationgroupusersubscription(notification_group_id, user_id) VALUES(%s,%s)",
                [ng, user],
            )
        self.db.delete_table("main_notificationgroupuser")
        self.db.delete_table("main_notificationgroupother")
