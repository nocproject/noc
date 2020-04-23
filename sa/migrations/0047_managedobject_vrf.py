# ----------------------------------------------------------------------
# managedobject vrf
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("ip", "0001_initial")]

    def migrate(self):
        VRF = self.db.mock_model(model_name="VRF", db_table="ip_vrf")
        self.db.add_column(
            "sa_managedobject",
            "vrf",
            models.ForeignKey(VRF, null=True, blank=True, on_delete=models.CASCADE),
        )
