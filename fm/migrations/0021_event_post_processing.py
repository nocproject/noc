
from south.db import db
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        EventClass = db.mock_model(model_name='EventClass', db_table='fm_eventclass', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        EventPriority = db.mock_model(model_name='EventPriority', db_table='fm_eventpriority', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        EventCategory = db.mock_model(model_name='EventCategory', db_table='fm_eventcategory', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EventPostProcessingRule'
        db.create_table('fm_eventpostprocessingrule', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event_class', models.ForeignKey(EventClass,verbose_name="Event Class")),
            ('name', models.CharField("Name",max_length=64)),
            ('preference', models.IntegerField("Preference",default=1000)),
            ('is_active', models.BooleanField("Is Active",default=True)),
            ('description', models.TextField("Description",blank=True,null=True)),
            ('change_priority', models.ForeignKey(EventPriority,verbose_name="Change Priority to",blank=True,null=True)),
            ('change_category', models.ForeignKey(EventCategory,verbose_name="Change Category to",blank=True,null=True)),
            ('action', models.CharField("Action",max_length=1,choices=[("A","Make Active"),("C","Close"),("D","Drop")],default="A"))
        ))
        
        # Mock Models
        EventPostProcessingRule = db.mock_model(model_name='EventPostProcessingRule', db_table='fm_eventpostprocessingrule', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EventPostProcessingRE'
        db.create_table('fm_eventpostprocessingre', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rule', models.ForeignKey(EventPostProcessingRule,verbose_name="Event Post-Processing Rule")),
            ('var_re', models.CharField("Var RE",max_length=256)),
            ('value_re', models.CharField("Value RE",max_length=256))
        ))
        
        db.send_create_signal('fm', ['EventPostProcessingRule','EventPostProcessingRE'])
    
    def backwards(self):
        db.delete_table('fm_eventpostprocessingre')
        db.delete_table('fm_eventpostprocessingrule')
        
