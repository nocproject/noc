
from south.db import db
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'ReduceTask'
        db.create_table('sa_reducetask', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('start_time', models.DateTimeField("Start Time")),
            ('stop_time', models.DateTimeField("Stop Time")),
            ('reduce_script', models.CharField("Script",max_length=256)),
            ('script_params', PickledField("Params",null=True,blank=True))
        ))
        
        # Mock Models
        ReduceTask = db.mock_model(model_name='ReduceTask', db_table='sa_reducetask', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ManagedObject = db.mock_model(model_name='ManagedObject', db_table='sa_managedobject', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'MapTask'
        db.create_table('sa_maptask', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('task', models.ForeignKey(ReduceTask,verbose_name="Task")),
            ('managed_object', models.ForeignKey(ManagedObject,verbose_name="Managed Object")),
            ('map_script', models.CharField("Script",max_length=256)),
            ('script_params', PickledField("Params",null=True,blank=True)),
            ('next_try', models.DateTimeField("Next Try")),
            ('retries_left', models.IntegerField("Retries Left",default=1)),
            ('status', models.CharField("Status",max_length=1,choices=[("W","Wait"),("R","Running"),("C","Complete"),("F","Failed")],default="W")),
            ('script_result', PickledField("Result",null=True,blank=True))
        ))
        
        db.send_create_signal('sa', ['ReduceTask','MapTask'])
    
    def backwards(self):
        db.delete_table('sa_maptask')
        db.delete_table('sa_reducetask')
        
