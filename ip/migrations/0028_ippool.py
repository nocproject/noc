# -*- coding: utf-8 -*-
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

    depends_on = (("sa", "0082_termination_group"),)

    def migrate(self):
        AFI_CHOICES = [("4", "IPv4"), ("6", "IPv6")]
        VRF = self.db.mock_model(
            model_name="VRF", db_table="ip_vrf", db_tablespace="", pk_field_name="id", pk_field_type=models.AutoField
        )
        TerminationGroup = self.db.mock_model(
            model_name="TerminationGroup",
            db_table="sa_terminationgroup",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        # Adding model "IPv4AddressRange"
        self.db.create_table(
            "ip_ippool", (
                ("id", models.AutoField(primary_key=True)),
                ("termination_group", models.ForeignKey(TerminationGroup, verbose_name="Termination Group")),
                ("vrf", models.ForeignKey(VRF, verbose_name="VRF")),
                ("afi", models.CharField("Address Family", max_length=1, choices=AFI_CHOICES)),
                ("type", models.CharField("Type", max_length=1, choices=[("D", "Dynamic"), ("S", "Static")])),
                ("from_address", models.IPAddressField("From Address")),
                ("to_address", models.IPAddressField("To Address"))
            )
        )
