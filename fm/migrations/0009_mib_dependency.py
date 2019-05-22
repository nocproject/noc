# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# mib dependency
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

        # Mock Models
        MIB = self.db.mock_model(
            model_name='MIB', db_table='fm_mib', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField
        )

        # Model 'MIBDependency'
        self.db.create_table(
            'fm_mibdependency', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('mib', models.ForeignKey(MIB, verbose_name=MIB)),
                ('requires_mib', models.ForeignKey(MIB, verbose_name="Requires MIB", related_name="requiredbymib_set"))
            )
        )
        self.db.create_index('fm_mibdependency', ['mib_id', 'requires_mib_id'], unique=True)
