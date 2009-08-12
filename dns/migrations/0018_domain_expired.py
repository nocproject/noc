# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.main.models import *

class Migration:
    depends_on=(
        ("main","0018_systemnotification"),
    )
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",["dns.domain_expired"])[0][0]==0:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)",["dns.domain_expired"])
        if db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",["dns.domain_expiration_warning"])[0][0]==0:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)",["dns.domain_expiration_warning"])
    
    def backwards(self):
        "Write your backwards migration here"
