
from south.db import db
from noc.kb.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        Language = db.mock_model(model_name='Language', db_table='main_language', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'KBEntryTemplate'
        db.create_table('kb_kbentrytemplate', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=128,unique=True)),
            ('subject', models.CharField("Subject",max_length=256)),
            ('body', models.TextField("Body")),
            ('language', models.ForeignKey(Language,verbose_name=Language,limit_choices_to={"is_active":True})),
            ('markup_language', models.CharField("Markup Language",max_length="16",choices=parser_registry.choices))
        ))
        # Mock Models
        KBEntryTemplate = db.mock_model(model_name='KBEntryTemplate', db_table='kb_kbentrytemplate', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        KBCategory = db.mock_model(model_name='KBCategory', db_table='kb_kbcategory', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'KBEntryTemplate.categories'
        db.create_table('kb_kbentrytemplate_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('kbentrytemplate', models.ForeignKey(KBEntryTemplate, null=False)),
            ('kbcategory', models.ForeignKey(KBCategory, null=False))
        )) 
        
        db.send_create_signal('kb', ['KBEntryTemplate'])
    
    def backwards(self):
        db.delete_table('kb_kbentrytemplate')
        
        db.delete_table('kb_kbentrytemplate_categories')
