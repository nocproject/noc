# ----------------------------------------------------------------------
# dnsserver and type
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

        # Model 'DNSServer'
        self.db.create_table(
            "dns_dnsserver",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=64, unique=True)),
                (
                    "description",
                    models.CharField("Description", max_length=128, blank=True, null=True),
                ),
                ("location", models.CharField("Location", max_length=128, blank=True, null=True)),
            ),
        )
        # M2M field 'DNSZoneProfile.ns_servers'
        DNSZoneProfile = self.db.mock_model(
            model_name="DNSZoneProfile", db_table="dns_dnszoneprofile"
        )
        DNSServer = self.db.mock_model(model_name="DNSServer", db_table="dns_dnsserver")
        self.db.create_table(
            "dns_dnszoneprofile_ns_servers",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "dnszoneprofile",
                    models.ForeignKey(DNSZoneProfile, null=False, on_delete=models.CASCADE),
                ),
                ("dnsserver", models.ForeignKey(DNSServer, null=False, on_delete=models.CASCADE)),
            ),
        )
