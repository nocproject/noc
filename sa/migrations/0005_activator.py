# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'Activator'
        db.create_table('sa_activator', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('ip', models.IPAddressField("IP")),
            ('auth', models.CharField("Auth String",max_length=64)),
            ('is_active', models.BooleanField("Is Active",default=True))
        ))
        
        db.send_create_signal('sa', ['Activator'])
    
    def backwards(self):
        db.delete_table('sa_activator')
        
