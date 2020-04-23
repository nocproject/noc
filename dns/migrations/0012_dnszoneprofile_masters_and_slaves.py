# ----------------------------------------------------------------------
# dnszoneprofile masters and slaves
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
        # Mock Models
        DNSZoneProfile = self.db.mock_model(
            model_name="DNSZoneProfile", db_table="dns_dnszoneprofile"
        )
        DNSServer = self.db.mock_model(model_name="DNSServer", db_table="dns_dnsserver")

        # M2M field 'DNSZoneProfile.masters'
        self.db.create_table(
            "dns_dnszoneprofile_masters",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "dnszoneprofile",
                    models.ForeignKey(DNSZoneProfile, null=False, on_delete=models.CASCADE),
                ),
                ("dnsserver", models.ForeignKey(DNSServer, null=False, on_delete=models.CASCADE)),
            ),
        )
        # Mock Models
        DNSZoneProfile = self.db.mock_model(
            model_name="DNSZoneProfile", db_table="dns_dnszoneprofile"
        )
        DNSServer = self.db.mock_model(model_name="DNSServer", db_table="dns_dnsserver")

        # M2M field 'DNSZoneProfile.slaves'
        self.db.create_table(
            "dns_dnszoneprofile_slaves",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "dnszoneprofile",
                    models.ForeignKey(DNSZoneProfile, null=False, on_delete=models.CASCADE),
                ),
                ("dnsserver", models.ForeignKey(DNSServer, null=False, on_delete=models.CASCADE)),
            ),
        )
        self.db.execute(
            """INSERT INTO dns_dnszoneprofile_masters(dnszoneprofile_id,dnsserver_id)
               SELECT dnszoneprofile_id,dnsserver_id
               FROM dns_dnszoneprofile_ns_servers"""
        )
        self.db.delete_table("dns_dnszoneprofile_ns_servers")
