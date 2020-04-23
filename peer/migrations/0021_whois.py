# ----------------------------------------------------------------------
# whois
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
        # Adding model 'WhoisDatabase'
        self.db.create_table(
            "peer_whoisdatabase",
            (
                ("id", models.AutoField(primary_key=True)),
                ("name", models.CharField("Name", max_length=32, unique=True)),
            ),
        )
        WhoisDatabase = self.db.mock_model(
            model_name="WhoisDatabase", db_table="peer_whoisdatabase"
        )

        # Adding model 'WhoisLookup'
        self.db.create_table(
            "peer_whoislookup",
            (
                ("id", models.AutoField(primary_key=True)),
                (
                    "whois_database",
                    models.ForeignKey(
                        WhoisDatabase, verbose_name="Whois Database", on_delete=models.CASCADE
                    ),
                ),
                ("url", models.CharField("Object", max_length=256)),
                ("direction", models.CharField("Direction", max_length=1)),
                ("key", models.CharField("Key", max_length=32)),
                ("value", models.CharField("Value", max_length=32)),
            ),
        )
        WhoisLookup = self.db.mock_model(model_name="WhoisLookup", db_table="peer_whoislookup")

        # Adding model 'WhoisCache'
        self.db.create_table(
            "peer_whoiscache",
            (
                ("id", models.AutoField(primary_key=True)),
                (
                    "lookup",
                    models.ForeignKey(
                        WhoisLookup, verbose_name="Whois Lookup", on_delete=models.CASCADE
                    ),
                ),
                ("key", models.CharField("Key", max_length=64)),
                ("value", models.TextField("Value")),
            ),
        )

        # Creating unique_together for [lookup, key] on WhoisCache.
        self.db.create_index("peer_whoiscache", ["lookup_id", "key"], unique=True)

        # Creating unique_together for [object, key, value] on WhoisLookup.
        self.db.create_index(
            "peer_whoislookup", ["whois_database_id", "url", "key", "value"], unique=True
        )
