# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        # Adding field 'UserAccess.selector'
        ManagedObjectSelector=db.mock_model(model_name="ManagedObjectSelector",db_table="sa_managedobjectselector")
        db.create_table('sa_managedobjectselectorbyattribute', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('selector', models.ForeignKey(ManagedObjectSelector,verbose_name="Object Selector")),
            ('key_re',   models.CharField("Filter by key (REGEXP)", max_length=256)),
            ('value_re', models.CharField("Filter by value (REGEXP)", max_length=256))
        ))
    
    def backwards(self):
        # Deleting field 'UserAccess.selector'
        db.delete_table('sa_managedobjectselectorbyattribute')
    
