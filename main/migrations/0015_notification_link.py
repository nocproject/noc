# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.main.models import *

class Migration:
    
    def forwards(self):
        db.add_column("main_notification","link",models.CharField("Link",max_length=256,null=True,blank=True))
    
    def backwards(self):
        db.delete_column("main_notification","link")
