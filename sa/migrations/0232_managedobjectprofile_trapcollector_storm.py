# ----------------------------------------------------------------------
# ManagedObjectProfile Trapcollector Storm policy and treshold
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobjectprofile",
            "trapcollector_storm_policy",
            models.CharField(
                "Trapcollector Storm Policy",
                max_length=1,
                choices=[
                    ("D", "Disabled"),
                    ("B", "Block"),
                    ("R", "Raise Alarm"),
                    ("A", "Block & Raise Alarm"),
                ],
                default="D",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "trapcollector_storm_threshold",
            models.IntegerField(default=1000),
        )
