
from south.db import db
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        # Mock models
        ManagedObjectSelector = db.mock_model(model_name="ManagedObjectSelector",
            db_table="sa_managedobjectselector", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        
        # Model "ReduceTask"
        db.create_table("sa_commandsnippet", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("name", models.CharField("Name", max_length = 128, unique = True)),
            ("description", models.TextField("Description")),
            ("snippet", models.TextField("Snippet")),
            ("change_configuration", models.BooleanField("Change configuration",
                    default=False)),
            ("selector", models.ForeignKey(ManagedObjectSelector,
                                         verbose_name="Object Selector")),
            ("is_enabled", models.BooleanField("Is Enabled?", default=True)),
            ("timeout", models.IntegerField("Timeout", default=60)),
            ("tags", AutoCompleteTagsField("Tags", null=True, blank=True)),
        ))
        
        db.send_create_signal("sa", ["CommandSnippet"])
    
    def backwards(self):
        db.delete_table("sa_commandsnippet")
    
