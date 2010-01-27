# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.sa.models import *

class Migration:
    
    def forwards(self, orm):
        db.execute("UPDATE sa_managedobject SET profile_name='Alcatel.OS62xx' WHERE profile_name='Alcatel.AOS'")
    
    def backwards(self, orm):
        db.execute("UPDATE sa_managedobject SET profile_name='Alcatel.AOS' WHERE profile_name='Alcatel.OS62xx'")
    
    models = {
    }
    
    complete_apps = ['sa']
