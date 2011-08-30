# encoding: utf-8
import datetime
from south.db import db
from django.db import models

class Migration:

    def forwards(self):
        PyRule = db.mock_model(model_name="PyRule", db_table="main_pyrule", db_tablespace="", pk_field_name="id", pk_field_type=models.AutoField)
        db.add_column("sa_managedobject", "config_filter_rule", models.ForeignKey(PyRule, verbose_name="Config Filter pyRule", null=True, blank=True))
        db.add_column("sa_managedobject", "config_validation_rule", models.ForeignKey(PyRule, verbose_name="Config Validation pyRule", null=True, blank=True))
    
    def backwards(self):
        db.delete_column("sa_managedobject", "config_filter_rule_id")
        db.delete_column("sa_managedobject", "config_validation_rule_id")
    
