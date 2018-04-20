
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
        # Model 'Language'
        db.create_table('main_language', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('native_name', models.CharField("Native Name",max_length=32)),
            ('is_active', models.BooleanField("Is Active",default=False))
        ))
<<<<<<< HEAD

        db.send_create_signal('main', ['Language'])

    def backwards(self):
        db.delete_table('main_language')

=======
        
        db.send_create_signal('main', ['Language'])
    
    def backwards(self):
        db.delete_table('main_language')
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
