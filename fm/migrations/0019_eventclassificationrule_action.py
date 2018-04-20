
from south.db import db
<<<<<<< HEAD
from django.db import models


class Migration:

=======
from noc.fm.models import *

class Migration:
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def forwards(self):
        db.add_column("fm_eventclassificationrule","action",models.CharField("Action",max_length=1,choices=[("A","Make Active"),("C","Close"),("D","Drop")],default="A"))
        db.execute("UPDATE fm_eventclassificationrule SET action='D' WHERE drop_event=TRUE")

    def backwards(self):
        db.delete_column("fm_eventclassificationrule","action")
