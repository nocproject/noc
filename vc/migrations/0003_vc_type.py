# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc type
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration

vc_checks = {
    "q": ("802.1Q VLAN", 1, (1, 4095), None),
    "Q": ("802.1ad Q-in-Q", 2, (1, 4095), (1, 4095)),
    "D": ("FR DLCI", 1, (16, 991), None),
    "M": ("MPLS", 1, (16, 1048575), (16, 1048575)),
    "A": ("ATM VCI/VPI", 1, (0, 65535), (0, 4095)),
    "X": ("X.25 group/channel", 2, (0, 15), (0, 255)),
}


class Migration(BaseMigration):
    def migrate(self):
        # Save old VCs
        vc_data = self.db.execute(
            "SELECT vc_domain_id,type,l1,l2,description FROM vc_vc ORDER by id"
        )
        # Delete old VC table
        self.db.delete_table("vc_vc")
        # Model 'VCType'
        self.db.create_table(
            "vc_vctype",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                ("name", models.CharField("Name", max_length=32, unique=True)),
                ("min_labels", models.IntegerField("Min. Labels", default=1)),
                ("label1_min", models.IntegerField("Label1 min")),
                ("label1_max", models.IntegerField("Label1 max")),
                ("label2_min", models.IntegerField("Label2 min", null=True, blank=True)),
                ("label2_max", models.IntegerField("Label2 max", null=True, blank=True)),
            ),
        )

        # Mock Models
        VCDomain = self.db.mock_model(model_name="VCDomain", db_table="vc_vcdomain")
        VCType = self.db.mock_model(model_name="VCType", db_table="vc_vctype")

        # Model 'VC'
        self.db.create_table(
            "vc_vc",
            (
                ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
                (
                    "vc_domain",
                    models.ForeignKey(VCDomain, verbose_name="VC Domain", on_delete=models.CASCADE),
                ),
                ("type", models.ForeignKey(VCType, verbose_name="type", on_delete=models.CASCADE)),
                ("l1", models.IntegerField("Label 1")),
                ("l2", models.IntegerField("Label 2", default=0)),
                ("description", models.CharField("Description", max_length=256)),
            ),
        )
        self.db.create_index("vc_vc", ["vc_domain_id", "type_id", "l1", "l2"], unique=True)

        # Fill in VC types
        vc_map = {}  # letter -> id
        for vt, d in vc_checks.items():
            name, min_labels, l1, l2 = d
            if l2 is None:
                l2 = (0, 0)
            self.db.execute(
                """INSERT INTO vc_vctype(name,min_labels,label1_min,label1_max,label2_min,label2_max)
                VALUES(%s,%s,%s,%s,%s,%s)""",
                [name, min_labels, l1[0], l1[1], l2[0], l2[1]],
            )
            vct_id = self.db.execute("SELECT id FROM vc_vctype WHERE name=%s", [name])[0][0]
            vc_map[vt] = vct_id
        # Return saved VC data
        for vc_domain_id, type, l1, l2, description in vc_data:
            self.db.execute(
                "INSERT INTO vc_vc(vc_domain_id,type_id,l1,l2,description) VALUES(%s,%s,%s,%s,%s)",
                [vc_domain_id, vc_map[type], l1, l2, description],
            )
