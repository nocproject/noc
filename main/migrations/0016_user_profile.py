# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.main.models import *

class Migration:
    
    def forwards(self):
        TimePattern = db.mock_model(model_name='TimePattern', db_table='main_timepattern', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        Language = db.mock_model(model_name='Language', db_table='main_language', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Adding model 'UserProfile'
        db.create_table('main_userprofile', (
            ('id', models.AutoField(primary_key=True)),
            ('preferred_language', models.ForeignKey(Language, null=True, verbose_name="Preferred Language", blank=True)),
            ('user', models.ForeignKey(User, unique=True)),
        ))
        db.send_create_signal('main', ['UserProfile'])
        UserProfile = db.mock_model(model_name='UserProfile', db_table='main_userprofile', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)

        # Adding model 'UserProfileContact'
        db.create_table('main_userprofilecontact', (
            ('user_profile', models.ForeignKey(UserProfile, verbose_name="User Profile")),
            ('notification_method', models.CharField("Method", max_length=16)),
            ('params', models.CharField("Params", max_length=256)),
            ('time_pattern', models.ForeignKey(TimePattern, verbose_name="Time Pattern")),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('main', ['UserProfileContact'])
        # Creating unique_together for [user_profile, time_pattern, notification_method, params] on UserProfileContact.
        db.create_index('main_userprofilecontact', ['user_profile_id', 'time_pattern_id', 'notification_method', 'params'],unique=True)
        
        
    
    
    def backwards(self):
        
        # Deleting model 'UserProfileContact'
        db.delete_table('main_userprofilecontact')
        
        # Deleting model 'UserProfile'
        db.delete_table('main_userprofile')
