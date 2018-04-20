
from south.db import db
<<<<<<< HEAD
from django.db import models

class Migration:

    def forwards(self):

=======
from noc.main.models import *

class Migration:
    
    def forwards(self):
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Model 'MIMEType'
        db.create_table('main_mimetype', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('extension', models.CharField("Extension",max_length=32,unique=True)),
            ('mime_type', models.CharField("MIME Type",max_length=63))
        ))
<<<<<<< HEAD

        db.send_create_signal('main', ['MIMEType'])

    def backwards(self):
        db.delete_table('main_mimetype')

=======
        
        db.send_create_signal('main', ['MIMEType'])
    
    def backwards(self):
        db.delete_table('main_mimetype')
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
