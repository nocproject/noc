# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

class Migration:
<<<<<<< HEAD

    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='NSN.hiX56xx' WHERE profile_name='Siemens.HIX5630'")

=======
    
    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='NSN.hiX56xx' WHERE profile_name='Siemens.HIX5630'")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        pass
