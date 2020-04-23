# ----------------------------------------------------------------------
# peering point enable provisioning
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
        NotificationGroup = self.db.mock_model(
            model_name="NotificationGroup", db_table="main_notificationgroup"
        )
        self.db.add_column(
            "peer_peeringpoint",
            "enable_prefix_list_provisioning",
            models.BooleanField("Enable Prefix-List Provisioning", default=False),
        )
        self.db.add_column(
            "peer_peeringpoint",
            "prefix_list_notification_group",
            models.ForeignKey(
                NotificationGroup,
                verbose_name="Prefix List Notification Group",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        )
