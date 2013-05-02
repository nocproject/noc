# -*- coding: utf-8 -*-

from south.db import db


class Migration:
    def forwards(self):
        for c in ["generator_name", "location",
                  "provisioning", "autozones_path"]:
            db.delete_column("dns_dnsserver", c)

    def backwards(self):
        pass
