# ----------------------------------------------------------------------
# managedobjectprofile alarm settings
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
            "box_discovery_alarm_policy",
            models.CharField(
                "Box Discovery Alarm Policy",
                max_length=1,
                choices=[("E", "Enable"), ("D", "Disable")],
                default="E",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_alarm_policy",
            models.CharField(
                "Periodic Discovery Alarm Policy",
                max_length=1,
                choices=[("E", "Enable"), ("D", "Disable")],
                default="E",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_fatal_alarm_weight",
            models.IntegerField("Box Fatal Alarm Weight", default=10),
        )

        self.db.add_column(
            "sa_managedobjectprofile",
            "box_discovery_alarm_weight",
            models.IntegerField("Box Alarm Weight", default=1),
        )

        self.db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_fatal_alarm_weight",
            models.IntegerField("Box Fatal Alarm Weight", default=10),
        )

        self.db.add_column(
            "sa_managedobjectprofile",
            "periodic_discovery_alarm_weight",
            models.IntegerField("Periodic Alarm Weight", default=1),
        )

        # Object settings
        self.db.add_column(
            "sa_managedobject",
            "box_discovery_alarm_policy",
            models.CharField(
                "Box Discovery Alarm Policy",
                max_length=1,
                choices=[("E", "Enable"), ("D", "Disable"), ("P", "From Profile")],
                default="P",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "periodic_discovery_alarm_policy",
            models.CharField(
                "Periodic Discovery Alarm Policy",
                max_length=1,
                choices=[("E", "Enable"), ("D", "Disable"), ("P", "From Profile")],
                default="P",
            ),
        )
