# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

class Migration:
<<<<<<< HEAD

    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",["sa.version_inventory"])[0][0]==0:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)",["sa.version_inventory"])

=======
    
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",["sa.version_inventory"])[0][0]==0:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)",["sa.version_inventory"])
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        "Write your backwards migration here"
