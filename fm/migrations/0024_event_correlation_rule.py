
from south.db import db
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.delete_table('fm_eventcorrelationrule')
        
        # Model 'EventCorrelationRule'
        db.create_table('fm_eventcorrelationrule', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True)),
            ('description', models.TextField("Description",null=True,blank=True)),
            ('is_builtin', models.BooleanField("Is Builtin",default=False)),
            ('rule_type', models.CharField("Rule Type",max_length=32,choices=[("Pair","Pair")])),
            ('action', models.CharField("Action",max_length=1,choices=[("C","Close"),("D","Drop"),("P","Root (parent)"),("c","Root (child)")])),
            ('same_object', models.BooleanField("Same Object",default=True)),
            ('window', models.IntegerField("Window (sec)",default=0))
        ))
        
        # Mock Models
        EventCorrelationRule = db.mock_model(model_name='EventCorrelationRule', db_table='fm_eventcorrelationrule', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        EventClass = db.mock_model(model_name='EventClass', db_table='fm_eventclass', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EventCorrelationMatchedClass'
        db.create_table('fm_eventcorrelationmatchedclass', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rule', models.ForeignKey(EventCorrelationRule,verbose_name="Rule")),
            ('event_class', models.ForeignKey(EventClass,verbose_name="Event Class"))
        ))
        db.create_index('fm_eventcorrelationmatchedclass', ['rule_id','event_class_id'], unique=True, db_tablespace='')
        
        
        # Mock Models
        EventCorrelationRule = db.mock_model(model_name='EventCorrelationRule', db_table='fm_eventcorrelationrule', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EventCorrelationMatchedVar'
        db.create_table('fm_eventcorrelationmatchedvar', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rule', models.ForeignKey(EventCorrelationRule,verbose_name="Rule")),
            ('var', models.CharField("Variable Name",max_length=256))
        ))
        db.create_index('fm_eventcorrelationmatchedvar', ['rule_id','var'], unique=True, db_tablespace='')
        
        
        db.send_create_signal('fm', ['EventCorrelationRule','EventCorrelationMatchedClass','EventCorrelationMatchedVar'])
    
    def backwards(self):
        db.delete_table('fm_eventcorrelationmatchedvar')
        db.delete_table('fm_eventcorrelationmatchedclass')
        db.delete_table('fm_eventcorrelationrule')
        
