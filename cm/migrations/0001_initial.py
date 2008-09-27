
from south.db import db
from noc.cm.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'ObjectCategory'
        db.create_table('cm_objectcategory', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True)),
            ('description', models.CharField("Description",max_length=128,null=True,blank=True))
        ))
        # Model 'Object'
        db.create_table('cm_object', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('handler_class_name', models.CharField("Object Type",max_length=64,choices=handler_choices)),
            ('stream_url', models.CharField("URL",max_length=128)),
            ('profile_name', models.CharField("Profile",max_length=128,choices=profile_choices)),
            ('repo_path', models.CharField("Repo Path",max_length=128)),
            ('last_pushed', models.DateTimeField("Last Pushed",blank=True,null=True)),
            ('last_pulled', models.DateTimeField("Last Pulled",blank=True,null=True))
        ))
        # Mock Models
        Object = db.mock_model(model_name='Object', db_table='cm_object', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ObjectCategory = db.mock_model(model_name='ObjectCategory', db_table='cm_objectcategory', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'Object.categories'
        db.create_table('cm_object_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('object', models.ForeignKey(Object, null=False)),
            ('objectcategory', models.ForeignKey(ObjectCategory, null=False))
        )) 
        db.create_index('cm_object', ['handler_class_name','repo_path'], unique=True, db_tablespace='')
        
        
        db.send_create_signal('cm', ['ObjectCategory','Object'])
    
    def backwards(self):
        db.delete_table('cm_object_categories')
        db.delete_table('cm_object')
        db.delete_table('cm_objectcategory')
