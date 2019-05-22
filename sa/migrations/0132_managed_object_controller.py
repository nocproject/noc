# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject controller
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
        ManagedObject = self.db.mock_model(
            model_name="ManagedObject",
            db_table="sa_managedobject",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )

        self.db.add_column(
            "sa_managedobject", "controller",
            models.ForeignKey(ManagedObject, verbose_name="Controller", blank=True, null=True)
        )
        self.db.add_column("sa_managedobject", "last_seen", models.DateTimeField("Last Seen", blank=True, null=True))
