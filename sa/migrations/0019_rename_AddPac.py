# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='AddPac.APOS' WHERE profile_name='VoiceFinder.AddPack'")
    
    def backwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='VoiceFinder.AddPack' WHERE profile_name='AddPac.APOS'")
