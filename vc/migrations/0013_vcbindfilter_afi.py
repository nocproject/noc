# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self):
        db.add_column("vc_vcbindfilter","afi",models.CharField("Address Family",max_length=1,choices=[("4","IPv4"),("6","IPv6")],default="4"))

    def backwards(self):
        db.delete_column("vc_vcbindfilter","afi")
