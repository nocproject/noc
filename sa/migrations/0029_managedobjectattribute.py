# encoding: utf-8
import datetime
from south.db import db
from django.db import models

class Migration:

    def forwards(self):
        ManagedObject = db.mock_model(model_name="ManagedObject", db_table="sa_managedobject", db_tablespace="", pk_field_name="id", pk_field_type=models.AutoField)
        
        # Model "MapTask"
        db.create_table("sa_managedobjectattribute", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("managed_object", models.ForeignKey(ManagedObject,verbose_name="Managed Object")),
            ("key", models.CharField(_("Key"),max_length=64)),
            ("value", models.CharField(_("Value"),max_length=4096, blank=True, null=True))
        ))
        db.create_index("sa_managedobjectattribute", ["managed_object_id", "key"], unique=True, db_tablespace="")
        
        db.send_create_signal("sa", ["ManagedObjectAttribute"])
    
    def backwards(self):
        db.delete_table("sa_managedobjectattribute")
    
