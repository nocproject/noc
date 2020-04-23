# ----------------------------------------------------------------------
# Address/Prefix.source
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
            "ip_prefix",
            "source",
            models.CharField(
                "Source",
                max_length=1,
                choices=[("M", "Manual"), ("i", "Interface"), ("n", "Neighbor")],
                null=False,
                blank=False,
                default="M",
            ),
        )
        self.db.add_column(
            "ip_address",
            "source",
            models.CharField(
                "Source",
                max_length=1,
                choices=[
                    ("M", "Manual"),
                    ("i", "Interface"),
                    ("m", "Management"),
                    ("n", "Neighbor"),
                ],
                null=False,
                blank=False,
                default="M",
            ),
        )
        self.db.add_column(
            "ip_address",
            "subinterface",
            models.CharField("SubInterface", max_length=128, null=True, blank=True),
        )
