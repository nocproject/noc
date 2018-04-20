
from south.db import db
<<<<<<< HEAD
from django.db import models


class Migration:

    def forwards(self):

        # Model 'EventCorrelationRule'
        db.create_table('fm_eventcorrelationrule', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name", max_length=64, unique=True)),
            ('rule', models.TextField("Rule")),
            ('description', models.TextField("Description", null=True, blank=True)),
            ('is_builtin', models.BooleanField("Is Builtin", default=False))
        ))

        db.send_create_signal('fm', ['EventCorrelationRule'])

    def backwards(self):
        db.delete_table('fm_eventcorrelationrule')
=======
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'EventCorrelationRule'
        db.create_table('fm_eventcorrelationrule', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True)),
            ('rule', models.TextField("Rule")),
            ('description', models.TextField("Description",null=True,blank=True)),
            ('is_builtin', models.BooleanField("Is Builtin",default=False))
        ))
        
        db.send_create_signal('fm', ['EventCorrelationRule'])
    
    def backwards(self):
        db.delete_table('fm_eventcorrelationrule')
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
