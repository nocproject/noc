
from south.db import db
<<<<<<< HEAD
from django.db import models
from noc.core.model.fields import TextArrayField

class Migration:

    def forwards(self):

        db.delete_table('main_refbookdata')

        # Mock Models
        RefBook = db.mock_model(model_name='RefBook', db_table='main_refbook', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)

=======
from noc.main.models import *
from noc.lib.fields import TextArrayField

class Migration:
    
    def forwards(self):
        
        db.delete_table('main_refbookdata')
        
        # Mock Models
        RefBook = db.mock_model(model_name='RefBook', db_table='main_refbook', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Model 'RefBookData'
        db.create_table('main_refbookdata', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ref_book', models.ForeignKey(RefBook,verbose_name="Ref Book")),
            ('value', TextArrayField("Value"))
        ))
<<<<<<< HEAD

        db.send_create_signal('main', ['RefBookData'])

        db.execute("UPDATE main_refbook SET next_update='now'")

=======
        
        db.send_create_signal('main', ['RefBookData'])
        
        db.execute("UPDATE main_refbook SET next_update='now'")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.delete_table('main_refbookdata')
        RefBook = db.mock_model(model_name='RefBook', db_table='main_refbook', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        RefBookField = db.mock_model(model_name='RefBookField', db_table='main_refbookfield', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
<<<<<<< HEAD

=======
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Model 'RefBookData'
        db.create_table('main_refbookdata', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ref_book', models.ForeignKey(RefBook,verbose_name="Ref Book")),
            ('record_id', models.IntegerField("ID")),
            ('field', models.ForeignKey(RefBookField,verbose_name="Field")),
            ('value', models.TextField("Value",null=True,blank=True))
        ))
<<<<<<< HEAD

=======
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
