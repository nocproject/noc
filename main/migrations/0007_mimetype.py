
from south.db import db
from django.db import models

class Migration:

    def forwards(self):

        # Model 'MIMEType'
        db.create_table('main_mimetype', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('extension', models.CharField("Extension",max_length=32,unique=True)),
            ('mime_type', models.CharField("MIME Type",max_length=63))
        ))

        db.send_create_signal('main', ['MIMEType'])

    def backwards(self):
        db.delete_table('main_mimetype')

