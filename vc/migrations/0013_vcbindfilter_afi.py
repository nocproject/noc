# encoding: utf-8
from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("vc_vcbindfilter", "afi",
                      models.CharField("Address Family", max_length=1, choices=[("4", "IPv4"), ("6", "IPv6")],
                                       default="4"))

    def backwards(self):
        db.delete_column("vc_vcbindfilter", "afi")
