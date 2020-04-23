# ----------------------------------------------------------------------
# ipv4addressrange
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
        VRF = self.db.mock_model(model_name="VRF", db_table="ip_vrf")
        # Adding model 'IPv4AddressRange'
        self.db.create_table(
            "ip_ipv4addressrange",
            (
                ("id", models.AutoField(primary_key=True)),
                ("vrf", models.ForeignKey(VRF, verbose_name="VRF", on_delete=models.CASCADE)),
                ("name", models.CharField("Name", max_length=64)),
                ("from_ip", models.GenericIPAddressField("From IP", protocol="IPv4")),
                ("to_ip", models.GenericIPAddressField("To Address", protocol="IPv4")),
                ("description", models.TextField("Description", null=True, blank=True)),
                ("is_locked", models.BooleanField("Range is locked", default=False)),
                ("fqdn_action", models.CharField("FQDN Action", default="N", max_length=1)),
                (
                    "fqdn_action_parameter",
                    models.CharField(
                        "FQDN Action Parameter", max_length=128, null=True, blank=True
                    ),
                ),
            ),
        )

        # Creating unique_together for [vrf, name] on IPv4AddressRange.
        self.db.create_index("ip_ipv4addressrange", ["vrf_id", "name"], unique=True)
