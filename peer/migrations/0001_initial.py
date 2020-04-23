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
    def migrate(self):
        # Model 'LIR'
        self.db.create_table(
            "peer_lir",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("LIR name", unique=True, max_length=64)),
            ),
        )

        # Mock Models
        LIR = self.db.mock_model(model_name="LIR", db_table="peer_lir")

        # Model 'AS'
        self.db.create_table(
            "peer_as",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("lir", models.ForeignKey(LIR, verbose_name=LIR, on_delete=models.CASCADE)),
                ("asn", models.IntegerField("ASN", unique=True)),
                ("description", models.CharField("Description", max_length=64)),
                ("rpsl_header", models.TextField("RPSL Header", null=True, blank=True)),
                ("rpsl_footer", models.TextField("RPSL Footer", null=True, blank=True)),
            ),
        )
        # Model 'ASSet'
        self.db.create_table(
            "peer_asset",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=32, unique=True)),
                ("description", models.CharField("Description", max_length=64)),
                ("members", models.TextField("Members", null=True, blank=True)),
                ("rpsl_header", models.TextField("RPSL Header", null=True, blank=True)),
                ("rpsl_footer", models.TextField("RPSL Footer", null=True, blank=True)),
            ),
        )
        # Model 'PeeringPointType'
        self.db.create_table(
            "peer_peeringpointtype",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=32, unique=True)),
            ),
        )

        # Mock Models
        PeeringPointType = self.db.mock_model(
            model_name="PeeringPointType", db_table="peer_peeringpointtype"
        )

        # Model 'PeeringPoint'
        self.db.create_table(
            "peer_peeringpoint",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("hostname", models.CharField("FQDN", max_length=64, unique=True)),
                (
                    "router_id",
                    models.GenericIPAddressField("Router-ID", unique=True, protocol="IPv4"),
                ),
                (
                    "type",
                    models.ForeignKey(
                        PeeringPointType, verbose_name="Type", on_delete=models.CASCADE
                    ),
                ),
                (
                    "communities",
                    models.CharField("Import Communities", max_length=128, blank=True, null=True),
                ),
            ),
        )
        # Model 'PeerGroup'
        self.db.create_table(
            "peer_peergroup",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=32, unique=True)),
                ("description", models.CharField("Description", max_length=64)),
                (
                    "communities",
                    models.CharField("Import Communities", max_length=128, blank=True, null=True),
                ),
                ("max_prefixes", models.IntegerField("Max. Prefixes", default=100)),
            ),
        )

        # Mock Models
        PeerGroup = self.db.mock_model(model_name="PeerGroup", db_table="peer_peergroup")
        PeeringPoint = self.db.mock_model(model_name="PeeringPoint", db_table="peer_peeringpoint")
        AS = self.db.mock_model(model_name="AS", db_table="peer_as")

        # Model 'Peer'
        self.db.create_table(
            "peer_peer",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "peer_group",
                    models.ForeignKey(
                        PeerGroup, verbose_name="Peer Group", on_delete=models.CASCADE
                    ),
                ),
                (
                    "peering_point",
                    models.ForeignKey(
                        PeeringPoint, verbose_name="Peering Point", on_delete=models.CASCADE
                    ),
                ),
                (
                    "local_asn",
                    models.ForeignKey(AS, verbose_name="Local AS", on_delete=models.CASCADE),
                ),
                ("local_ip", models.GenericIPAddressField("Local IP", protocol="IPv4")),
                ("remote_asn", models.IntegerField("Remote AS")),
                ("remote_ip", models.GenericIPAddressField("Remote IP", protocol="IPv4")),
                ("import_filter", models.CharField("Import filter", max_length=64)),
                ("local_pref", models.IntegerField("Local Pref", null=True, blank=True)),
                ("export_filter", models.CharField("Export filter", max_length=64)),
                (
                    "description",
                    models.CharField("Description", max_length=64, null=True, blank=True),
                ),
                ("tt", models.IntegerField("TT", blank=True, null=True)),
                (
                    "communities",
                    models.CharField("Import Communities", max_length=128, blank=True, null=True),
                ),
                ("max_prefixes", models.IntegerField("Max. Prefixes", default=100)),
            ),
        )
