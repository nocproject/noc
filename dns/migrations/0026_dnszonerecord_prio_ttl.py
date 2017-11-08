# -*- coding: utf-8 -*-

from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("dns_dnszonerecord", "priority",
                      models.IntegerField(_("Priority"), null=True, blank=True))
        db.add_column("dns_dnszonerecord", "ttl",
                      models.IntegerField(_("TTL"), null=True, blank=True))

    def backwards(self):
        db.delete_column("dns_dnszonerecord", "priority")
        db.delete_column("dns_dnszonerecord", "ttl")
