# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.main.models import *

class Migration:
    def forwards(self):
        # Adding model 'Permission'
        db.create_table('main_permission', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=128,unique=True)),
        ))
        db.send_create_signal('main', ['Permission'])
        Permission = db.mock_model(model_name='Permission', db_table='main_permission', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Adding ManyToManyField 'Permission.groups'
        Group = db.mock_model(model_name='Group', db_table='auth_group', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.create_table('main_permission_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('permission', models.ForeignKey(Permission, null=False)),
            ('group', models.ForeignKey(Group, null=False))
        ))
        
        # Adding ManyToManyField 'Permission.users'
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.create_table('main_permission_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('permission', models.ForeignKey(Permission, null=False)),
            ('user', models.ForeignKey(User, null=False))
        ))

    def backwards(self):
        # Deleting model 'Permission'
        db.delete_table('main_permission')
        # Dropping ManyToManyField 'Permission.groups'
        db.delete_table('main_permission_groups')
        # Dropping ManyToManyField 'Permission.users'
        db.delete_table('main_permission_users')
