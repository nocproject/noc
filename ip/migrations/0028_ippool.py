# ----------------------------------------------------------------------
# ippool
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("sa", "0082_termination_group")]

    def migrate(self):
        AFI_CHOICES = [("4", "IPv4"), ("6", "IPv6")]
        VRF = self.db.mock_model(model_name="VRF", db_table="ip_vrf")
        TerminationGroup = self.db.mock_model(
            model_name="TerminationGroup", db_table="sa_terminationgroup"
        )
        # Adding model "IPv4AddressRange"
        self.db.create_table(
            "ip_ippool",
            (
                ("id", models.AutoField(primary_key=True)),
                (
                    "termination_group",
                    models.ForeignKey(
                        TerminationGroup, verbose_name="Termination Group", on_delete=models.CASCADE
                    ),
                ),
                ("vrf", models.ForeignKey(VRF, verbose_name="VRF", on_delete=models.CASCADE)),
                ("afi", models.CharField("Address Family", max_length=1, choices=AFI_CHOICES)),
                (
                    "type",
                    models.CharField(
                        "Type", max_length=1, choices=[("D", "Dynamic"), ("S", "Static")]
                    ),
                ),
                ("from_address", models.GenericIPAddressField("From Address", protocol="IPv4")),
                ("to_address", models.GenericIPAddressField("To Address", protocol="IPv4")),
            ),
        )
