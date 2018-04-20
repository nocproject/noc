# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
<<<<<<< HEAD
from django.db import models

class Migration:

    def forwards(self):
        db.add_column("main_notification","link",models.CharField("Link",max_length=256,null=True,blank=True))

=======
from noc.main.models import *

class Migration:
    
    def forwards(self):
        db.add_column("main_notification","link",models.CharField("Link",max_length=256,null=True,blank=True))
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.delete_column("main_notification","link")
