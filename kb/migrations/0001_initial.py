
from south.db import db
<<<<<<< HEAD
from noc.kb.models.kbentry import models
=======
from noc.kb.models import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

class Migration:
    depends_on=(
        ("main","0004_language"),
    )
    def forwards(self):
<<<<<<< HEAD

=======
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Model 'KBCategory'
        db.create_table('kb_kbcategory', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True))
        ))
<<<<<<< HEAD

        # Mock Models
        Language = db.mock_model(model_name='Language', db_table='main_language', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)

=======
        
        # Mock Models
        Language = db.mock_model(model_name='Language', db_table='main_language', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Model 'KBEntry'
        db.create_table('kb_kbentry', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('subject', models.CharField("Subject",max_length=256)),
            ('body', models.TextField("Body")),
            ('language', models.ForeignKey(Language,verbose_name=Language)),
            ('markup_language', models.CharField("Markup Language",max_length="16"))
        ))
        # Mock Models
        KBEntry = db.mock_model(model_name='KBEntry', db_table='kb_kbentry', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        KBCategory = db.mock_model(model_name='KBCategory', db_table='kb_kbcategory', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
<<<<<<< HEAD

=======
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # M2M field 'KBEntry.categories'
        db.create_table('kb_kbentry_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('kbentry', models.ForeignKey(KBEntry, null=False)),
            ('kbcategory', models.ForeignKey(KBCategory, null=False))
        )) 
<<<<<<< HEAD

        # Mock Models
        KBEntry = db.mock_model(model_name='KBEntry', db_table='kb_kbentry', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)

=======
        
        # Mock Models
        KBEntry = db.mock_model(model_name='KBEntry', db_table='kb_kbentry', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Model 'KBEntryHistory'
        db.create_table('kb_kbentryhistory', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('kb_entry', models.ForeignKey(KBEntry,verbose_name="KB Entry")),
            ('timestamp', models.DateTimeField("Timestamp",auto_now_add=True)),
            ('user', models.ForeignKey(User,verbose_name=User)),
            ('diff', models.TextField("Diff"))
        ))
<<<<<<< HEAD

        db.send_create_signal('kb', ['KBCategory','KBEntry','KBEntryHistory'])

=======
        
        db.send_create_signal('kb', ['KBCategory','KBEntry','KBEntryHistory'])
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.delete_table('kb_kbentryhistory')
        db.delete_table('kb_kbentry_categories')
        db.delete_table('kb_kbcategory')
        db.delete_table('kb_kbentry')
