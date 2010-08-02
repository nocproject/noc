# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.sa.models import *

class Migration:
    
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
    
    def backwards(self):
        # Deleting model 'GroupAccess'
        db.delete_table('sa_groupaccess')
