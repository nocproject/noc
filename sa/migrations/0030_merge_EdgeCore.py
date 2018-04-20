# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

class Migration:
<<<<<<< HEAD

    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='EdgeCore.ES' WHERE profile_name LIKE 'EdgeCore.ES%%'")

=======
    
    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='EdgeCore.ES' WHERE profile_name LIKE 'EdgeCore.ES%%'")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        pass
