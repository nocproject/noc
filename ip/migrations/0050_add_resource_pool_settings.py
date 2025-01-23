# ----------------------------------------------------------------------
# Add pools to IP Prefix Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "ip_prefix",
            "pools",
            models.JSONField(
                "Remote System mappings",
                null=True,
                blank=True,
                default=lambda: "[]",
            ),
        )
        self.db.add_column(
            "ip_prefix",
            "default_address_profile",
            DocumentReferenceField("ip.AddressProfile", null=True, blank=True),
        )
        self.db.add_column(
            "ip_address",
            "allocated_user",
            models.CharField(
                "Allocated User",
                max_length=256,
                null=True,
                blank=True,
            ),
        )
