
from south.db import db
from noc.main.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'NotificationGroup'
        db.create_table('main_notificationgroup', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True)),
            ('description', models.TextField("Description",null=True,blank=True))
        ))
        
        # Mock Models
        NotificationGroup = db.mock_model(model_name='NotificationGroup', db_table='main_notificationgroup', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        TimePattern = db.mock_model(model_name='TimePattern', db_table='main_timepattern', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'NotificationGroupUser'
        db.create_table('main_notificationgroupuser', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('notification_group', models.ForeignKey(NotificationGroup,verbose_name="Notification Group")),
            ('time_pattern', models.ForeignKey(TimePattern,verbose_name="Time Pattern")),
            ('user', models.ForeignKey(User,verbose_name=User))
        ))
        db.create_index('main_notificationgroupuser', ['notification_group_id','time_pattern_id','user_id'], unique=True, db_tablespace='')
        
        
        # Mock Models
        NotificationGroup = db.mock_model(model_name='NotificationGroup', db_table='main_notificationgroup', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        TimePattern = db.mock_model(model_name='TimePattern', db_table='main_timepattern', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'NotificationGroupOther'
        db.create_table('main_notificationgroupother', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('notification_group', models.ForeignKey(NotificationGroup,verbose_name="Notification Group")),
            ('time_pattern', models.ForeignKey(TimePattern,verbose_name="Time Pattern")),
            ('notification_method', models.CharField("Method",max_length=16)),
            ('params', models.CharField("Params",max_length=256))
        ))
        db.create_index('main_notificationgroupother', ['notification_group_id','time_pattern_id','notification_method','params'], unique=True, db_tablespace='')
        
        # Model 'Notification'
        db.create_table('main_notification', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('timestamp', models.DateTimeField("Timestamp",auto_now=True,auto_now_add=True)),
            ('notification_method', models.CharField("Method",max_length=16)),
            ('notification_params', models.CharField("Params",max_length=256)),
            ('subject', models.CharField("Subject",max_length=256)),
            ('body', models.TextField("Body")),
            ('next_try', models.DateTimeField("Next Try",null=True,blank=True)),
            ('actual_till', models.DateTimeField("Actual Till",null=True,blank=True))
        ))
        
        db.send_create_signal('main', ['NotificationGroup','NotificationGroupUser','NotificationGroupOther','Notification'])
    
    def backwards(self):
        db.delete_table('main_notification')
        db.delete_table('main_notificationgroupother')
        db.delete_table('main_notificationgroupuser')
        db.delete_table('main_notificationgroup')
        
