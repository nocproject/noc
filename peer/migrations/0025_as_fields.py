# ----------------------------------------------------------------------
# as fields
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("ip", "0004_default_vrf")]

    def migrate(self):
        rx_remarks = re.compile(r"^remarks:\s*")

        RIR = self.db.mock_model(model_name="RIR", db_table="peer_rir")
        AS = self.db.mock_model(model_name="AS", db_table="peer_as")
        Person = self.db.mock_model(model_name="Person", db_table="peer_person")
        Maintainer = self.db.mock_model(model_name="Maintainer", db_table="peer_maintainer")

        self.db.create_table(
            "peer_organisation",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("organisation", models.CharField("Organisation", max_length=128, unique=True)),
                ("org_name", models.CharField("Org. Name", max_length=128)),
                (
                    "org_type",
                    models.CharField("Org. Type", max_length=64, choices=[("LIR", "LIR")]),
                ),
                ("address", models.TextField("Address")),
                (
                    "mnt_ref",
                    models.ForeignKey(
                        Maintainer, verbose_name="Mnt. Ref", on_delete=models.CASCADE
                    ),
                ),
            ),
        )

        Organisation = self.db.mock_model(model_name="Organisation", db_table="peer_organisation")

        self.db.add_column(
            "peer_as",
            "rir",
            models.ForeignKey(RIR, null=True, blank=True, on_delete=models.CASCADE),
        )
        self.db.add_column(
            "peer_as",
            "organisation",
            models.ForeignKey(Organisation, null=True, blank=True, on_delete=models.CASCADE),
        )
        self.db.add_column(
            "peer_as", "header_remarks", models.TextField("Header Remarks", null=True, blank=True)
        )
        self.db.add_column(
            "peer_as", "footer_remarks", models.TextField("Footer Remarks", null=True, blank=True)
        )

        # Adding ManyToManyField 'AS.maintainers'
        self.db.create_table(
            "peer_as_maintainers",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("as", models.ForeignKey(AS, null=False, on_delete=models.CASCADE)),
                ("maintainer", models.ForeignKey(Maintainer, null=False, on_delete=models.CASCADE)),
            ),
        )

        # Adding ManyToManyField 'AS.tech_contacts'
        self.db.create_table(
            "peer_as_tech_contacts",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("as", models.ForeignKey(AS, null=False, on_delete=models.CASCADE)),
                ("person", models.ForeignKey(Person, null=False, on_delete=models.CASCADE)),
            ),
        )

        # Adding ManyToManyField 'AS.routes_maintainers'
        self.db.create_table(
            "peer_as_routes_maintainers",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("as", models.ForeignKey(AS, null=False, on_delete=models.CASCADE)),
                ("maintainer", models.ForeignKey(Maintainer, null=False, on_delete=models.CASCADE)),
            ),
        )

        # Adding ManyToManyField 'AS.administrative_contacts'
        self.db.create_table(
            "peer_as_administrative_contacts",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("as", models.ForeignKey(AS, null=False, on_delete=models.CASCADE)),
                ("person", models.ForeignKey(Person, null=False, on_delete=models.CASCADE)),
            ),
        )

        # Fill out RIR
        ripe_id = self.db.execute("SELECT id FROM peer_rir WHERE name=%s", ["RIPE NCC"])[0]
        self.db.execute("UPDATE peer_as SET rir_id=%s", [ripe_id])
        # Fill out organisation
        mnt_id = self.db.execute("SELECT id FROM peer_maintainer LIMIT 1")[0][0]
        self.db.execute(
            "INSERT INTO peer_organisation(organisation,org_name,org_type,address,mnt_ref_id) VALUES(%s,%s,%s,%s,%s)",
            ["ORG-DEFAULT", "Default Organisation", "LIR", "Anywhere", mnt_id],
        )
        org_id = self.db.execute("SELECT id FROM peer_organisation LIMIT 1")[0][0]
        self.db.execute("UPDATE peer_as SET organisation_id=%s", [org_id])
        # Migrate headers and footers
        for id, rpsl_header, rpsl_footer in self.db.execute(
            "SELECT id,rpsl_header,rpsl_footer FROM peer_as"
        ):
            header_remarks = rpsl_header
            if header_remarks:
                header_remarks = "\n".join([rx_remarks.sub("", x) for x in rpsl_header.split("\n")])
            footer_remarks = rpsl_footer
            if footer_remarks:
                footer_remarks = "\n".join([rx_remarks.sub("", x) for x in rpsl_footer.split("\n")])
            self.db.execute(
                "UPDATE peer_as SET header_remarks=%s,footer_remarks=%s WHERE id=%s",
                [header_remarks, footer_remarks, id],
            )
        self.db.execute("COMMIT")
        self.db.delete_column("peer_as", "maintainer_id")
        self.db.delete_column("peer_as", "routes_maintainer_id")
        self.db.delete_column("peer_as", "rpsl_header")
        self.db.delete_column("peer_as", "rpsl_footer")
        self.db.execute("ALTER TABLE peer_as ALTER rir_id SET NOT NULL")
        self.db.execute("ALTER TABLE peer_as ALTER organisation_id SET NOT NULL")
