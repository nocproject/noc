# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

class Migration:
<<<<<<< HEAD

    def forwards(self):
        db.execute("UPDATE auth_user SET is_staff=TRUE WHERE is_staff=FALSE")

=======
    
    def forwards(self):
        db.execute("UPDATE auth_user SET is_staff=TRUE WHERE is_staff=FALSE")
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        "Write your backwards migration here"
