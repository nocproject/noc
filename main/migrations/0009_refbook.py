
from south.db import db
from noc.main.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        Language = db.mock_model(model_name='Language', db_table='main_language', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'RefBook'
        db.create_table('main_refbook', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=128,unique=True)),
            ('language', models.ForeignKey(Language,verbose_name=Language)),
            ('description', models.TextField("Description",blank=True,null=True)),
            ('is_enabled', models.BooleanField("Is Enabled",default=False)),
            ('is_builtin', models.BooleanField("Is Builtin",default=False)),
            ('downloader', models.CharField("Downloader",max_length=64,blank=True,null=True)),
            ("download_url", models.CharField("Download URL",max_length=256,null=True,blank=True)),
            ('last_updated', models.DateTimeField("Last Updated",blank=True,null=True)),
            ('next_update', models.DateTimeField("Next Update",blank=True,null=True)),
            ('refresh_interval', models.IntegerField("Refresh Interval (days)",default=0))
        ))
        
        # Mock Models
        RefBook = db.mock_model(model_name='RefBook', db_table='main_refbook', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'RefBookField'
        db.create_table('main_refbookfield', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ref_book', models.ForeignKey(RefBook,verbose_name="Ref Book")),
            ('name', models.CharField("Name",max_length="64")),
            ('order', models.IntegerField("Order")),
            ('is_required', models.BooleanField("Is Required",default=True)),
            ('description', models.TextField("Description",blank=True,null=True)),
            ('search_method', models.CharField("Search Method",max_length=64,blank=True,null=True)),
        ))
        db.create_index('main_refbookfield', ['ref_book_id','order'], unique=True, db_tablespace='')
        
        db.create_index('main_refbookfield', ['ref_book_id','name'], unique=True, db_tablespace='')
        
        
        # Mock Models
        RefBook = db.mock_model(model_name='RefBook', db_table='main_refbook', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        RefBookField = db.mock_model(model_name='RefBookField', db_table='main_refbookfield', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'RefBookData'
        db.create_table('main_refbookdata', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ref_book', models.ForeignKey(RefBook,verbose_name="Ref Book")),
            ('record_id', models.IntegerField("ID")),
            ('field', models.ForeignKey(RefBookField,verbose_name="Field")),
            ('value', models.TextField("Value",null=True,blank=True))
        ))
        db.create_index('main_refbookdata', ['ref_book_id','record_id','field_id'], unique=True, db_tablespace='')
        
        
        db.send_create_signal('main', ['RefBook','RefBookField','RefBookData'])
    
    def backwards(self):
        db.delete_table('main_refbookdata')
        db.delete_table('main_refbookfield')
        db.delete_table('main_refbook')
        
