# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from south.db import db


class Migration:
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def forwards(self):
        # Adding model 'GroupAccess'
        Group=db.mock_model(model_name="Group",db_table="auth_group")
        ManagedObjectSelector=db.mock_model(model_name="ManagedObjectSelector",db_table="sa_managedobjectselector")
        db.create_table('sa_groupaccess', (
            ('id', models.AutoField(primary_key=True)),
            ('group', models.ForeignKey(Group,verbose_name="Group")),
            ('selector', models.ForeignKey(ManagedObjectSelector,verbose_name="Object Selector")),
        ))
        db.send_create_signal('sa', ['GroupAccess'])
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        # Deleting model 'GroupAccess'
        db.delete_table('sa_groupaccess')
