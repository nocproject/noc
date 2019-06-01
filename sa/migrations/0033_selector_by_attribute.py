# ----------------------------------------------------------------------
# selector by attribute
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
        # Adding field 'UserAccess.selector'
        ManagedObjectSelector = self.db.mock_model(model_name="ManagedObjectSelector", db_table="sa_managedobjectselector")
        self.db.create_table(
            'sa_managedobjectselectorbyattribute', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('selector', models.ForeignKey(ManagedObjectSelector, verbose_name="Object Selector")),
                ('key_re', models.CharField("Filter by key (REGEXP)", max_length=256)),
                ('value_re', models.CharField("Filter by value (REGEXP)", max_length=256))
            )
        )
