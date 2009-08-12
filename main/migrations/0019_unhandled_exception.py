# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.main.models import *

class Migration:
    
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",["main.unhandled_exception"])[0][0]==0:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)",["main.unhandled_exception"])
    
    def backwards(self):
        "Write your backwards migration here"
