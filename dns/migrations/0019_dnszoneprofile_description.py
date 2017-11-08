# -*- coding: utf-8 -*-

from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("dns_dnszoneprofile", "description",
                      models.TextField("Description", blank=True, null=True))

    def backwards(self):
        db.delete_column("dns_dnszoneprofile", "description")
