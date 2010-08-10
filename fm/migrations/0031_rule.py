
from south.db import db
from noc.fm.models import *

class Migration:
    depends_on=(
        ("main","0022_pyrule_is_builtin"),
    )
    def forwards(self):
        PyRule=db.mock_model(model_name="PyRule",db_table="main_pyrule")
        db.add_column("fm_eventclass","rule",models.ForeignKey(PyRule,verbose_name="pyRule",null=True,blank=True))
        db.add_column("fm_eventpostprocessingrule","rule",models.ForeignKey(PyRule,verbose_name="pyRule",null=True,blank=True))
        db.delete_column("fm_eventclass","trigger")
    
    def backwards(self):
        db.delete_column("fm_eventclass","rule_id")
        db.delete_column("fm_eventpostprocessingrule","rule_id")
        db.add_column("fm_eventclass","trigger",models.CharField("Trigger",max_length=64,null=True,blank=True))
