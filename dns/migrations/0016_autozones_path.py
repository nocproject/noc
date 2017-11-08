from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("dns_dnsserver", "autozones_path",
                      models.CharField("Autozones path", max_length=256,
                                       blank=True, null=True, default="autozones"))

    def backwards(self):
        db.delete_column("dns_dnsserver", "autozones_path")
