<<<<<<< HEAD
# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

=======

from south.db import db
from noc.fm.models import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

class Migration:
    depends_on=(
        ("main","0022_pyrule_is_builtin"),
    )
<<<<<<< HEAD

=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def forwards(self):
        PyRule=db.mock_model(model_name="PyRule",db_table="main_pyrule")
        db.add_column("fm_eventclass","rule",models.ForeignKey(PyRule,verbose_name="pyRule",null=True,blank=True))
        db.add_column("fm_eventpostprocessingrule","rule",models.ForeignKey(PyRule,verbose_name="pyRule",null=True,blank=True))
        db.delete_column("fm_eventclass","trigger")
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.delete_column("fm_eventclass","rule_id")
        db.delete_column("fm_eventpostprocessingrule","rule_id")
        db.add_column("fm_eventclass","trigger",models.CharField("Trigger",max_length=64,null=True,blank=True))
