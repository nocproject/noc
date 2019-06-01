# ----------------------------------------------------------------------
# useraccess selector
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
        self.db.add_column(
            'sa_useraccess', 'selector',
            models.ForeignKey(ManagedObjectSelector, verbose_name="Object Selector", null=True, blank=True)
        )
        self.db.delete_column('sa_useraccess', 'administrative_domain_id')
        self.db.delete_column('sa_useraccess', 'group_id')
