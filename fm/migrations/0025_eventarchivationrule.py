
from south.db import db
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        # Mock Models
        EventClass = db.mock_model(model_name='EventClass', db_table='fm_eventclass', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EventArchivationRule'
        db.create_table('fm_eventarchivationrule', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event_class', models.ForeignKey(EventClass,verbose_name="Event Class",unique=True)),
            ('ttl', models.IntegerField("Time To Live")),
            ('ttl_measure', models.CharField("Measure",choices=[("s","Seconds"),("m","Minutes"),("h","Hours"),("d","Days")],default="h",max_length=1)),
            ('action', models.CharField("Action",choices=[("D","Drop")],default="D",max_length=1))
        ))
        
        db.send_create_signal('fm', ['EventArchivationRule'])
    
    def backwards(self):
        db.delete_table('fm_eventarchivationrule')
        
