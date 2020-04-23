# ----------------------------------------------------------------------
# ManagedObject.event_processing_policy
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
        # Profile settings
        self.db.add_column(
            "sa_managedobjectprofile",
            "event_processing_policy",
            models.CharField(
                "Event Processing Policy",
                max_length=1,
                choices=[("E", "Process Events"), ("D", "Drop events")],
                default="E",
            ),
        )
        # Object settings
        self.db.add_column(
            "sa_managedobject",
            "event_processing_policy",
            models.CharField(
                "Event Processing Policy",
                max_length=1,
                choices=[("P", "Profile"), ("E", "Process Events"), ("D", "Drop events")],
                default="P",
            ),
        )
