# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject vc_domain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("vc", "0001_initial")]

    def migrate(self):
        VCDomain = self.db.mock_model(
            model_name="VCDomain",
            db_table="vc_vcdomain",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        self.db.add_column("sa_managedobject", "vc_domain", models.ForeignKey(VCDomain, null=True, blank=True))
