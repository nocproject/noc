# ----------------------------------------------------------------------
# address mac
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.fields import MACField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("sa", "0007_managed_object")]

    def migrate(self):
        ManagedObject = self.db.mock_model(model_name="ManagedObject", db_table="sa_managedobject")
        self.db.add_column("ip_ipv4address", "mac", MACField("MAC", null=True, blank=True))
        self.db.add_column(
            "ip_ipv4address",
            "managed_object",
            models.ForeignKey(ManagedObject, null=True, blank=True, on_delete=models.CASCADE),
        )
        self.db.add_column(
            "ip_ipv4address",
            "auto_update_mac",
            models.BooleanField("Auto Update MAC", default=False),
        )
