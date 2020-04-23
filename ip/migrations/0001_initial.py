# ----------------------------------------------------------------------
# initial
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("peer", "0001_initial")]

    def migrate(self):

        # Model 'VRFGroup'
        self.db.create_table(
            "ip_vrfgroup",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("VRF Group", unique=True, max_length=64)),
                (
                    "unique_addresses",
                    models.BooleanField("Unique addresses in group", default=False),
                ),
            ),
        )

        # Mock Models
        VRFGroup = self.db.mock_model(model_name="VRFGroup", db_table="ip_vrfgroup")

        # Model 'VRF'
        self.db.create_table(
            "ip_vrf",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("VRF name", unique=True, max_length=64)),
                (
                    "vrf_group",
                    models.ForeignKey(VRFGroup, verbose_name="VRF Group", on_delete=models.CASCADE),
                ),
                ("rd", models.CharField("rd", unique=True, max_length=21)),
                ("tt", models.IntegerField("TT", blank=True, null=True)),
            ),
        )

        # Mock Models
        User = self.db.mock_model(model_name="User", db_table="auth_user")
        VRF = self.db.mock_model(model_name="VRF", db_table="ip_vrf")

        # Model 'IPv4BlockAccess'
        self.db.create_table(
            "ip_ipv4blockaccess",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("user", models.ForeignKey(User, verbose_name=User, on_delete=models.CASCADE)),
                ("vrf", models.ForeignKey(VRF, verbose_name=VRF, on_delete=models.CASCADE)),
                ("prefix", models.CharField("prefix", max_length=18)),
                ("tt", models.IntegerField("TT", blank=True, null=True)),
            ),
        )
        self.db.create_index("ip_ipv4blockaccess", ["user_id", "vrf_id", "prefix"], unique=True)

        # Mock Models
        VRF = self.db.mock_model(model_name="VRF", db_table="ip_vrf")
        AS = self.db.mock_model(model_name="AS", db_table="peer_as")
        User = self.db.mock_model(model_name="User", db_table="auth_user")

        # Model 'IPv4Block'
        self.db.create_table(
            "ip_ipv4block",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("description", models.CharField("Description", max_length=64)),
                ("prefix", models.CharField("prefix", max_length=18)),
                ("vrf", models.ForeignKey(VRF, on_delete=models.CASCADE)),
                ("asn", models.ForeignKey(AS, on_delete=models.CASCADE)),
                (
                    "modified_by",
                    models.ForeignKey(User, verbose_name=User, on_delete=models.CASCADE),
                ),
                (
                    "last_modified",
                    models.DateTimeField("Last modified", auto_now=True, auto_now_add=True),
                ),
                ("tt", models.IntegerField("TT", blank=True, null=True)),
            ),
        )
        self.db.create_index("ip_ipv4block", ["prefix", "vrf_id"], unique=True)

        # Mock Models
        VRF = self.db.mock_model(model_name="VRF", db_table="ip_vrf")
        User = self.db.mock_model(model_name="User", db_table="auth_user")

        # Model 'IPv4Address'
        self.db.create_table(
            "ip_ipv4address",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("vrf", models.ForeignKey(VRF, verbose_name=VRF, on_delete=models.CASCADE)),
                ("fqdn", models.CharField("FQDN", max_length=64)),
                ("ip", models.GenericIPAddressField("IP", protocol="IPv4")),
                (
                    "description",
                    models.CharField("Description", blank=True, null=True, max_length=64),
                ),
                (
                    "modified_by",
                    models.ForeignKey(User, verbose_name=User, on_delete=models.CASCADE),
                ),
                (
                    "last_modified",
                    models.DateTimeField("Last modified", auto_now=True, auto_now_add=True),
                ),
                ("tt", models.IntegerField("TT", blank=True, null=True)),
            ),
        )
        self.db.create_index("ip_ipv4address", ["vrf_id", "ip"], unique=True)
