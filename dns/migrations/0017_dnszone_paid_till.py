# -*- coding: utf-8 -*-

from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("dns_dnszone", "paid_till",
                      models.DateField("Paid Tille", null=True, blank=True))

    def backwards(self):
        db.delete_column("dns_dnszone", "paid_till")
