# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
<<<<<<< HEAD
from django.db import models

class Migration:

    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",["main.unhandled_exception"])[0][0]==0:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)",["main.unhandled_exception"])

=======
from noc.main.models import *

class Migration:
    
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",["main.unhandled_exception"])[0][0]==0:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)",["main.unhandled_exception"])
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        "Write your backwards migration here"
