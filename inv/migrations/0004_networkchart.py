# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# networkchart
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):

    depends_on = (('sa', '0056_managedobjectselecter_filter_object_profile'),)

    def migrate(self):
        ManagedObjectSelector = self.db.mock_model(
            model_name="ManagedObjectSelector",
            db_table="sa_managedobjectselector",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        self.db.create_table(
            'inv_networkchart', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField("Name", max_length=64, unique=True)),
                ('description', models.TextField("Description", blank=True, null=True)),
                ('is_active', models.BooleanField("Is Active", default=True)),
                ('selector', models.ForeignKey(ManagedObjectSelector))
            )
        )
