
from south.db import db
from noc.fm.models import *

class Migration:
    def forwards(self):
        # Mock Models
        Event = db.mock_model(model_name='Event', db_table='fm_event', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EventLog'
        db.create_table('fm_eventlog', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(Event,verbose_name=Event)),
            ('timestamp', models.DateTimeField("Timestamp")),
            ('from_status', models.CharField("From Status",max_length=1,choices=EVENT_STATUS_CHOICES)),
            ('to_status', models.CharField("To Status",max_length=1,choices=EVENT_STATUS_CHOICES)),
            ('message', models.TextField("Message"))
        ))
        db.send_create_signal('fm', ['EventLog'])
    
    def backwards(self):
        db.delete_table('fm_eventlog')
        
