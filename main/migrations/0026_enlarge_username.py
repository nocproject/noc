# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

class Migration:
<<<<<<< HEAD

    def forwards(self):
        db.execute("ALTER TABLE auth_user ALTER username TYPE VARCHAR(75)")

=======
    
    def forwards(self):
        db.execute("ALTER TABLE auth_user ALTER username TYPE VARCHAR(75)")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.execute("ALTER TABLE auth_user ALTER username TYPE VARCHAR(30)")
