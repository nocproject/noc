# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
<<<<<<< HEAD

=======
from noc.fm.models import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

class Migration:
    depends_on=(
        ("main","0015_notification_link"),
    )
<<<<<<< HEAD

=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def forwards(self):
        ManagedObjectSelector = db.mock_model(model_name='ManagedObjectSelector', db_table='sa_managedobjectselector', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        TimePattern = db.mock_model(model_name='TimePattern', db_table='main_timepattern', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        NotificationGroup = db.mock_model(model_name='NotificationGroup', db_table='main_notificationgroup', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
<<<<<<< HEAD

        db.add_column("fm_eventpostprocessingrule","managed_object_selector",models.ForeignKey(ManagedObjectSelector,verbose_name="Managed Object Selector",null=True,blank=True))
        db.add_column("fm_eventpostprocessingrule","time_pattern",models.ForeignKey(TimePattern,verbose_name="Time Pattern",null=True,blank=True))
        db.add_column("fm_eventpostprocessingrule","notification_group",models.ForeignKey(NotificationGroup,verbose_name="Notification Group",null=True,blank=True))

    def backwards(self):
        db.delete_column("fm_eventpostprocessingrule","notification_group_id")
        db.delete_column("fm_eventpostprocessingrule","time_pattern_id")
        db.delete_column("fm_eventpostprocessingrule","managed_object_selector_id")
=======
        
        db.add_column("fm_eventpostprocessingrule","managed_object_selector",models.ForeignKey(ManagedObjectSelector,verbose_name="Managed Object Selector",null=True,blank=True))
        db.add_column("fm_eventpostprocessingrule","time_pattern",models.ForeignKey(TimePattern,verbose_name="Time Pattern",null=True,blank=True))
        db.add_column("fm_eventpostprocessingrule","notification_group",models.ForeignKey(NotificationGroup,verbose_name="Notification Group",null=True,blank=True))
    
    def backwards(self):
        db.delete_column("fm_eventpostprocessingrule","notification_group_id")
        db.delete_column("fm_eventpostprocessingrule","time_pattern_id")
        db.delete_column("fm_eventpostprocessingrule","managed_object_selector_id")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
