# -*- coding: utf-8 -*-

from south.db import db
<<<<<<< HEAD


class Migration:

    def forwards(self):
        db.create_index("fm_event",["status"])
        db.create_index("fm_event",["timestamp"])

=======
from django.db import models
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.create_index("fm_event",["status"])
        db.create_index("fm_event",["timestamp"])
    
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.delete_index("fm_event",["status"])
        db.delete_index("fm_event",["timestamp"])
