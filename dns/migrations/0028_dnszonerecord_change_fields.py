# -*- coding: utf-8 -*-

from south.db import db
from django.db import models


class Migration:
    def forwards(self):
        db.rename_column("dns_dnszonerecord", "left", "name")
        db.rename_column("dns_dnszonerecord", "right", "content")
        db.execute("""
            ALTER TABLE dns_dnszonerecord
            ALTER COLUMN content TYPE VARCHAR(256)
            """)
        db.add_column("dns_dnszonerecord", "type",
            models.CharField(_("Type"), max_length=16, default=""))

    def backwards(self):
<<<<<<< HEAD
        pass
=======
        pass
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
