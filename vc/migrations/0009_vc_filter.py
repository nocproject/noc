# ----------------------------------------------------------------------
# vc filter
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
        # Adding model 'VCFilter'
        self.db.create_table(
            "vc_vcfilter",
            (
                ("id", models.AutoField(primary_key=True)),
                ("name", models.CharField("Name", unique=True, max_length=64)),
                ("expression", models.CharField("Expression", max_length=256)),
                ("description", models.TextField("Description", null=True, blank=True)),
            ),
        )
        # Add "Any VLAN filter"
        if self.db.execute("SELECT COUNT(*) FROM vc_vcfilter WHERE name='Any VLAN'")[0][0] == 0:
            self.db.execute(
                "INSERT INTO vc_vcfilter(name,expression) VALUES(%s,%s)", ["Any VLAN", "1-4095"]
            )
