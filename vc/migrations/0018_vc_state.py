# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VRF, Prefix, IP state
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = (("main", "0043_default_resourcestates"),)

    def migrate(self):
        # Create .state
        ResourceState = self.db.mock_model(
            model_name="ResourceState",
            db_table="main_resourcestate",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        self.db.add_column("vc_vc", "state",
                           models.ForeignKey(ResourceState, verbose_name="State", null=True, blank=True))
