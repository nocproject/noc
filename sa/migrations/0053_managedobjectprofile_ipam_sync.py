from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("sa_managedobjectprofile",
                      "sync_ipam", models.BooleanField("Sync. IPAM", default=False))
        db.add_column("sa_managedobjectprofile",
                      "fqdn_template", models.TextField("FQDN template",
                                                        null=True, blank=True))

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "sync_ipam")
        db.delete_column("sa_managedobjectprofile", "fqdn_template")
