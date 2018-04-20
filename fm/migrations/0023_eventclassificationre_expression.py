
from south.db import db
<<<<<<< HEAD
from django.db import models


class Migration:

    def forwards(self):
        db.add_column("fm_eventclassificationre","is_expression",models.BooleanField("Is Expression",default=False))

=======
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.add_column("fm_eventclassificationre","is_expression",models.BooleanField("Is Expression",default=False))
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.delete_column("fm_eventclassificationre","is_expression")
