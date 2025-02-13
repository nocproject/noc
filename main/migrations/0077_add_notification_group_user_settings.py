# ----------------------------------------------------------------------
# Add Notification Group Settings to User
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):

    def migrate(self):
        self.db.add_column(
            "main_notificationgroupusersubscription",
            "policy",
            models.CharField(
                max_length=1,
                choices=[
                    ("D", "Disable"),  # Direct
                    ("A", "Any"),
                    ("W", "By Types"),
                    ("W", "By Types"),
                ],
                default="A",
                null=False,
                blank=False,
            ),
        )
        self.db.add_column(
            "main_notificationgroupusersubscription",
            "title_tag",
            models.CharField(max_length=30, null=True, blank=True),
        )
        self.db.add_column(
            "main_notificationgroupusersubscription",
            "method",
            models.CharField(max_length=16, null=True, blank=True),
        )
