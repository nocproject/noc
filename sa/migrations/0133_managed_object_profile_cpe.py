# ----------------------------------------------------------------------
# managedobjectprofile cpe
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
        self.db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_cpe",
            models.BooleanField(default=False),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "cpe_segment_policy",
            models.CharField(
                "CPE Segment Policy",
                max_length=1,
                choices=[("C", "From controller"), ("L", "From linked object")],
                default="C",
            ),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "cpe_cooldown",
            models.IntegerField("CPE cooldown, days", default=0),
        )
