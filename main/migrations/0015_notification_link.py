# -*- coding: utf-8 -*-

from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("main_notification", "link", models.CharField("Link", max_length=256, null=True, blank=True))

    def backwards(self):
        db.delete_column("main_notification", "link")
