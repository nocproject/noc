
from south.db import db
<<<<<<< HEAD
from django.db import models


class Migration:

=======
from noc.fm.models import *

class Migration:
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def forwards(self):
        Event = db.mock_model(model_name='Event', db_table='fm_event', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.add_column("fm_event","status",models.CharField("Status",max_length=1,default="U"))
        db.add_column("fm_event","active_till",models.DateTimeField("Active Till",blank=True,null=True))
        db.add_column("fm_event","close_timestamp",models.DateTimeField("Close Timestamp",blank=True,null=True))
        db.add_column("fm_event","root",models.ForeignKey(Event,blank=True,null=True))
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.delete_column("fm_event","status")
        db.delete_column("fm_event","active_till")
        db.delete_column("fm_event","close_timestamp")
<<<<<<< HEAD
        db.delete_column("fm_event","root")
=======
        dv.delete_column("fm_event","root")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
