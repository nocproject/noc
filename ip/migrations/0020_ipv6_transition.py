# ---------------------------------------------------------------------
# PrefixTransition and AddressTransition
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        Prefix = self.db.mock_model(model_name="Prefix", db_table="ip_prefix")

        Address = self.db.mock_model(model_name="Address", db_table="ip_address")

        self.db.add_column(
            "ip_prefix",
            "ipv6_transition",
            models.OneToOneField(Prefix, null=True, blank=True, on_delete=models.CASCADE),
        )
        self.db.add_column(
            "ip_address",
            "ipv6_transition",
            models.OneToOneField(Address, null=True, blank=True, on_delete=models.CASCADE),
        )
