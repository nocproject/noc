
from south.db import db
from noc.main.models import *

class Migration:
    
    def forwards(self):
        db.delete_table('main_taskschedule')

    def backwards(self):
        # Model 'TaskSchedule'
        db.create_table('main_taskschedule', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('periodic_name', models.CharField("Periodic Task",max_length=64)),
            ('is_enabled', models.BooleanField("Enabled?",default=False)),
            ('run_every', models.PositiveIntegerField("Run Every (secs)",default=86400)),
            ('retries', models.PositiveIntegerField("Retries",default=1)),
            ('retry_delay', models.PositiveIntegerField("Retry Delay (secs)",default=60)),
            ('timeout', models.PositiveIntegerField("Timeout (secs)",default=300)),
            ('next_run', models.DateTimeField("Next Run",auto_now_add=True)),
            ('retries_left', models.PositiveIntegerField("Retries Left",default=1))
        ))
        
