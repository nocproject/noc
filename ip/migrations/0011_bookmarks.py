# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.ip.models import *

class Migration:
    
    def forwards(self):
        IPv4Block=db.mock_model(model_name='IPv4Block', db_table='ip_ipv4block', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        User=db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        # Adding model 'IPv4BlockBookmark'
        db.create_table('ip_ipv4blockbookmark', (
            ('id', models.AutoField(primary_key=True)),
            ('user', models.ForeignKey(User,verbose_name="User")),
            ('prefix', models.ForeignKey(IPv4Block,verbose_name="Prefix"))
        ))
        db.send_create_signal('ip', ['IPv4BlockBookmark'])
        
        # Creating unique_together for [user,prefix]
        db.create_unique('ip_ipv4blockbookmark', ['user_id', 'prefix_id'])
        
    
    
    def backwards(self):
        db.delete_unique('ip_ipv4blockbookmark', ['user_id', 'prefix_id'])
        db.delete_table('ip_ipv4blockbookmark')
