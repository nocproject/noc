# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        # Adding field 'UserAccess.selector'
        ManagedObjectSelector = db.mock_model(
            model_name="ManagedObjectSelector",
            db_table="sa_managedobjectselector")
        db.add_column('sa_useraccess', 'selector',
                      models.ForeignKey(ManagedObjectSelector,
                                        verbose_name="Object Selector", null=True, blank=True))
        db.delete_column('sa_useraccess', 'administrative_domain_id')
        db.delete_column('sa_useraccess', 'group_id')

    def backwards(self):
        # Deleting field 'UserAccess.selector'
        db.delete_column('sa_useraccess', 'selector_id')
