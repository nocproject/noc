
from south.db import db
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        AdministrativeDomain = db.mock_model(model_name='AdministrativeDomain', db_table='sa_administrativedomain', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'ManagedObjectSelector'
        db.create_table('sa_managedobjectselector', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True)),
            ('description', models.TextField("Description",blank=True,null=True)),
            ('is_enabled', models.BooleanField("Is Enabled",default=True)),
            ('filter_id', models.IntegerField("Filter by ID",null=True,blank=True)),
            ('filter_name', models.CharField("Filter by Name (REGEXP)",max_length=256,null=True,blank=True)),
            ('filter_profile', models.CharField("Filter by Profile",max_length=64,null=True,blank=True,choices=profile_registry.choices)),
            ('filter_address', models.CharField("Filter by Address (REGEXP)",max_length=256,null=True,blank=True)),
            ('filter_administrative_domain', models.ForeignKey(AdministrativeDomain,verbose_name="Filter by Administrative Domain",null=True,blank=True)),
            ('filter_user', models.CharField("Filter by User (REGEXP)",max_length=256,null=True,blank=True)),
            ('filter_remote_path', models.CharField("Filter by Remote Path (REGEXP)",max_length=256,null=True,blank=True)),
            ('filter_description', models.CharField("Filter by Description (REGEXP)",max_length=256,null=True,blank=True)),
            ('filter_repo_path', models.CharField("Filter by Repo Path (REGEXP)",max_length=256,null=True,blank=True)),
            ('source_combine_method', models.CharField("Source Combine Method",max_length=1,default="O",choices=[("A","AND"),("O","OR")]))
        ))
        # Mock Models
        ManagedObjectSelector = db.mock_model(model_name='ManagedObjectSelector', db_table='sa_managedobjectselector', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ObjectGroup = db.mock_model(model_name='ObjectGroup', db_table='sa_objectgroup', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'ManagedObjectSelector.filter_groups'
        db.create_table('sa_managedobjectselector_filter_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('managedobjectselector', models.ForeignKey(ManagedObjectSelector, null=False)),
            ('objectgroup', models.ForeignKey(ObjectGroup, null=False))
        )) 
        # Mock Models
        ManagedObjectSelector = db.mock_model(model_name='ManagedObjectSelector', db_table='sa_managedobjectselector', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ManagedObjectSelector = db.mock_model(model_name='ManagedObjectSelector', db_table='sa_managedobjectselector', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'ManagedObjectSelector.sources'
        db.create_table('sa_managedobjectselector_sources', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_managedobjectselector', models.ForeignKey(ManagedObjectSelector, null=False)),
            ('to_managedobjectselector', models.ForeignKey(ManagedObjectSelector, null=False))
        )) 
        
        db.send_create_signal('sa', ['ManagedObjectSelector'])
    
    def backwards(self):
        db.delete_table('sa_managedobjectselector_filter_groups')
        db.delete_table('sa_managedobjectselector_sources')
        db.delete_table('sa_managedobjectselector')

