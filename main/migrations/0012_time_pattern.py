
from south.db import db
from noc.main.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'TimePattern'
        db.create_table('main_timepattern', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True)),
            ('description', models.TextField("Description",null=True,blank=True))
        ))
        
        # Mock Models
        TimePattern = db.mock_model(model_name='TimePattern', db_table='main_timepattern', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'TimePatternTerm'
        db.create_table('main_timepatternterm', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('time_pattern', models.ForeignKey(TimePattern,verbose_name="Time Pattern")),
            ('term', models.CharField("Term",max_length=256))
        ))
        db.create_index('main_timepatternterm', ['time_pattern_id','term'], unique=True, db_tablespace='')
        db.send_create_signal('main', ['TimePattern','TimePatternTerm'])
    
    def backwards(self):
        db.delete_table('main_timepatternterm')
        db.delete_table('main_timepattern')
        
