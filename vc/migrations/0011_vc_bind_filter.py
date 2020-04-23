# ----------------------------------------------------------------------
# vc bind filter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.fields import CIDRField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("ip", "0001_initial")]

    def migrate(self):
        # Adding model 'VCBindFilter'
        VCDomain = self.db.mock_model(model_name="VCDomain", db_table="vc_vcdomain")
        VRF = self.db.mock_model(model_name="VRF", db_table="ip_vrf")
        VCFilter = self.db.mock_model(model_name="VCFilter", db_table="vc_vcfilter")
        self.db.create_table(
            "vc_vcbindfilter",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "vc_domain",
                    models.ForeignKey(VCDomain, verbose_name="VC Domain", on_delete=models.CASCADE),
                ),
                ("vrf", models.ForeignKey(VRF, verbose_name="VRF", on_delete=models.CASCADE)),
                ("prefix", CIDRField("Prefix")),
                (
                    "vc_filter",
                    models.ForeignKey(VCFilter, verbose_name="VC Filter", on_delete=models.CASCADE),
                ),
            ),
        )

        # Adding field 'VCDomain.enable_vc_bind_filter'
        self.db.add_column(
            "vc_vcdomain",
            "enable_vc_bind_filter",
            models.BooleanField("Enable VC Bind filter", default=False),
        )
