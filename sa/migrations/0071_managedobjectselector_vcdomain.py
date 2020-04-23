# ----------------------------------------------------------------------
# managedobjectselector vc_domain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("ip", "0001_initial"), ("vc", "0001_initial")]

    def migrate(self):
        VRF = self.db.mock_model(model_name="VRF", db_table="ip_vrf")
        VCDomain = self.db.mock_model(model_name="VCDomain", db_table="vc_vcdomain")
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_vrf",
            models.ForeignKey(
                VRF, verbose_name="Filter by VRF", null=True, blank=True, on_delete=models.CASCADE
            ),
        )
        self.db.add_column(
            "sa_managedobjectselector",
            "filter_vc_domain",
            models.ForeignKey(
                VCDomain,
                verbose_name="Filter by VC Domain",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        )
