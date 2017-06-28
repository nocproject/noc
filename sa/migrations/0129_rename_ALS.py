# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

class Migration:

    def forwards(self):
        db.execute("UPDATE sa_managedobject SET profile_name='Alsitec.7200' WHERE profile_name LIKE 'ALS.7200'")

    def backwards(self):
        pass
