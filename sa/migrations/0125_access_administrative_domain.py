# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# administrativedomain access
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
        AdministrativeDomain = self.db.mock_model(
            model_name="AdministrativeDomain",
            db_table="sa_administrativedomain",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        for t in ("sa_useraccess", "sa_groupaccess"):
            self.db.add_column(t, "administrative_domain", models.ForeignKey(AdministrativeDomain, null=True, blank=True))
            self.db.execute("ALTER TABLE %s ALTER selector_id DROP NOT NULL" % t)
