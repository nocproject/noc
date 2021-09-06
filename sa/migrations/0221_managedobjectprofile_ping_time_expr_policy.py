# ----------------------------------------------------------------------
# ManagedObjectProfile ping time expr policy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from django.db import models


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "sa_managedobjectprofile",
            "ping_time_expr_policy",
            models.CharField(
                "Ping Time Expr Policy",
                choices=[("D", "Disable ping"), ("E", "Enable ping but dont follow status")],
                max_length=1,
                default="D",
            ),
        )
