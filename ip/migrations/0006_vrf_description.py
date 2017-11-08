# -*- coding: utf-8 -*-

from django.db import models
from noc.ip.models import *
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("ip_vrfgroup", "description",
                      models.CharField("Description", blank=True, null=True, max_length=128))
        db.add_column("ip_vrf", "description", models.CharField("Description", blank=True, null=True, max_length=128))

    def backwards(self):
        db.delete_column("ip_vrfgroup", "description")
        db.delete_column("ip_vrf", "description")
