# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.vc.models import *

class Migration:
    
    def forwards(self):
        
        # Adding model 'VCFilter'
        db.create_table('vc_vcfilter', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField("Name", unique=True, max_length=64)),
            ('expression', models.CharField("Expression", max_length=256)),
            ('description', models.TextField("Description", null=True, blank=True)),
        ))
        db.send_create_signal('vc', ['VCFilter'])
        # Add "Any VLAN filter"
        if db.execute("SELECT COUNT(*) FROM vc_vcfilter WHERE name='Any VLAN'")[0][0]==0:
            db.execute("INSERT INTO vc_vcfilter(name,expression) VALUES(%s,%s)",["Any VLAN","1-4095"])
    
    def backwards(self):
        
        # Deleting model 'VCFilter'
        db.delete_table('vc_vcfilter')
