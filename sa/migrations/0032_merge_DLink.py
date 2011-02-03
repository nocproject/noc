# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.sa.models import *

class Migration:
    
    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='DLink.DxS' WHERE profile_name LIKE 'DLink.D_S3xxx'")
    
    def backwards(self):
        pass
