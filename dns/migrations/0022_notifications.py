# ----------------------------------------------------------------------
# notification
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
            "dns_dnszoneprofile",
            "notification_group",
            models.ForeignKey(NotificationGroup, blank=True, null=True, on_delete=models.CASCADE),
        )
        self.db.add_column(
            "dns_dnszone",
            "notification_group",
            models.ForeignKey(NotificationGroup, blank=True, null=True, on_delete=models.CASCADE),
        )
