# -*- coding: utf-8 -*-

from south.db import db
<<<<<<< HEAD


class Migration:

=======
from django.db import models
from noc.fm.models import *

class Migration:
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def forwards(self):
        db.create_unique('fm_eventarchivationrule', ['event_class_id', 'action'])
        try:
            db.delete_unique('fm_eventarchivationrule', ['event_class_id'])
        except:
            pass
<<<<<<< HEAD

    def backwards(self):
        db.delete_unique('fm_eventarchivationrule', ['event_class_id', 'action'])
        db.create_unique('fm_eventarchivationrule', ['event_class_id'])
=======
    
    def backwards(self):
        db.delete_unique('fm_eventarchivationrule', ['event_class_id', 'action'])
        db.create_unique('fm_eventarchivationrule', ['event_class_id'])
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
