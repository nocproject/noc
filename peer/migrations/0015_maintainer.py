# ----------------------------------------------------------------------
# maintainer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party models
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Model 'RIR'
        self.db.create_table(
            "peer_rir",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("name", max_length=64, unique=True)),
                ("whois", models.CharField("whois", max_length=64, blank=True, null=True)),
            ),
        )

        # Mock Models
        RIR = self.db.mock_model(model_name="RIR", db_table="peer_rir")

        # Model 'Person'
        self.db.create_table(
            "peer_person",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("nic_hdl", models.CharField("nic-hdl", max_length=64, unique=True)),
                ("person", models.CharField("person", max_length=128)),
                ("address", models.TextField("address")),
                ("phone", models.TextField("phone")),
                ("fax_no", models.TextField("fax-no", blank=True, null=True)),
                ("email", models.TextField("email")),
                ("rir", models.ForeignKey(RIR, verbose_name=RIR, on_delete=models.CASCADE)),
                ("extra", models.TextField("extra", blank=True, null=True)),
            ),
        )

        # Mock Models
        RIR = self.db.mock_model(model_name="RIR", db_table="peer_rir")

        # Model 'Maintainer'
        self.db.create_table(
            "peer_maintainer",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("maintainer", models.CharField("mntner", max_length=64, unique=True)),
                ("description", models.CharField("description", max_length=64)),
                ("auth", models.TextField("auth")),
                ("rir", models.ForeignKey(RIR, verbose_name=RIR, on_delete=models.CASCADE)),
                ("extra", models.TextField("extra", blank=True, null=True)),
            ),
        )
        # Mock Models
        Maintainer = self.db.mock_model(model_name="Maintainer", db_table="peer_maintainer")
        Person = self.db.mock_model(model_name="Person", db_table="peer_person")

        # M2M field 'Maintainer.admins'
        self.db.create_table(
            "peer_maintainer_admins",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("maintainer", models.ForeignKey(Maintainer, null=False, on_delete=models.CASCADE)),
                ("person", models.ForeignKey(Person, null=False, on_delete=models.CASCADE)),
            ),
        )

        for rir, whois in [
            ("ARIN", "whois.arin.net"),
            ("RIPE NCC", "whois.ripe.net"),
            ("APNIC", "whois.apnic.net"),
            ("LACNIC", "whois.lacnic.net"),
            ("AfriNIC", "whois.afrinic.net"),
        ]:
            self.db.execute("INSERT INTO peer_rir(name,whois) VALUES(%s,%s)", [rir, whois])
