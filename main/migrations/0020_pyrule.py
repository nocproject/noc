# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.main.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'PyRule'
        db.create_table('main_pyrule', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField("Name", unique=True, max_length=64)),
            ('interface', models.CharField("Interface", max_length=64)),
            ('description', models.TextField("Description")),
            ('text', models.TextField("Text")),
            ('changed', models.DateTimeField("Changed", auto_now=True, auto_now_add=True)),
        ))
        db.send_create_signal('main', ['PyRule'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'PyRule'
        db.delete_table('main_pyrule')
        
    
    
    models = {
        
    }
    
    
