
from south.db import db
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'EventPriority'
        db.create_table('fm_eventpriority', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('priority', models.IntegerField("Priority")),
            ('description', models.TextField("Description",blank=True,null=True))
        ))
        # Model 'EventClass'
        db.create_table('fm_eventclass', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('description', models.TextField("Description",blank=True,null=True))
        ))
        
        # Mock Models
        ManagedObject = db.mock_model(model_name='ManagedObject', db_table='sa_managedobject', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        EventPriority = db.mock_model(model_name='EventPriority', db_table='fm_eventpriority', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        EventClass = db.mock_model(model_name='EventClass', db_table='fm_eventclass', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        Event = db.mock_model(model_name='Event', db_table='fm_event', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'Event'
        db.create_table('fm_event', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('timestamp', models.DateTimeField("Timestamp")),
            ('managed_object', models.ForeignKey(ManagedObject,verbose_name="Managed Object")),
            ('event_priority', models.ForeignKey(EventPriority,verbose_name="Priority")),
            ('event_class', models.ForeignKey(EventClass,verbose_name="Event Class")),
            ('parent', models.ForeignKey(Event,verbose_name="Parent",blank=True,null=True)),
            ('subject', models.CharField("Subject",max_length=256,null=True,blank=True)),
            ('body', models.TextField("Body",null=True,blank=True))
        ))
        
        # Mock Models
        Event = db.mock_model(model_name='Event', db_table='fm_event', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EventData'
        db.create_table('fm_eventdata', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(Event,verbose_name=Event)),
            ('key', models.CharField("Key",max_length=64)),
            ('value', models.TextField("Value",blank=True,null=True))
        ))
        db.create_index('fm_eventdata', ['event_id','key'], unique=True, db_tablespace='')
        
        
        db.send_create_signal('fm', ['EventPriority','EventClass','Event','EventData'])
    
    def backwards(self):
        db.delete_table('fm_eventdata')
        db.delete_table('fm_event')
        db.delete_table('fm_eventclass')
        db.delete_table('fm_eventpriority')
        
