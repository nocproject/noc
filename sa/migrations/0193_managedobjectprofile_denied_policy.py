# ----------------------------------------------------------------------
# ManagedObjectProfile.denied_firmware_policy
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
        # ManagedObjectProfile
        self.db.add_column(
            "sa_managedobjectprofile",
            "new_platform_creation_policy",
            models.CharField(
                "New Platform Creation Policy",
                max_length=1,
                choices=[("C", "Create"), ("A", "Alarm")],
                default="C",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "denied_firmware_policy",
            models.CharField(
                "Firmware Policy",
                max_length=1,
                choices=[
                    ("I", "Ignore"),
                    ("s", "Ignore&Stop"),
                    ("A", "Raise Alarm"),
                    ("S", "Raise Alarm&Stop"),
                ],
                default="I",
            ),
        )
        # ManagedObject
        self.db.add_column(
            "sa_managedobject",
            "denied_firmware_policy",
            models.CharField(
                "Firmware Policy",
                max_length=1,
                choices=[
                    ("P", "Profile"),
                    ("I", "Ignore"),
                    ("s", "Ignore&Stop"),
                    ("A", "Raise Alarm"),
                    ("S", "Raise Alarm&Stop"),
                ],
                default="P",
            ),
        )
