# ----------------------------------------------------------------------
# object notify and notification group
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0017_initial_userprofilecontacts")]

    def migrate(self):
        NotificationGroup = self.db.mock_model(
            model_name="NotificationGroup", db_table="main_notificationgroup"
        )
        self.db.add_column(
            "cm_objectnotify",
            "notification_group",
            models.ForeignKey(
                NotificationGroup,
                verbose_name="Notification Group",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        )
