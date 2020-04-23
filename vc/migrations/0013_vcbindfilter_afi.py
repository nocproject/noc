# ----------------------------------------------------------------------
# vcbindfilter afi
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
            "vc_vcbindfilter",
            "afi",
            models.CharField(
                "Address Family", max_length=1, choices=[("4", "IPv4"), ("6", "IPv6")], default="4"
            ),
        )
