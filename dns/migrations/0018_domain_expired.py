# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# domain expired
# ----------------------------------------------------------------------
# Copyright (C) 2009-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    depends_on = (("main", "0018_systemnotification"),)

    def forwards(self):
        if not db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s", ["dns.domain_expired"])[0][0]:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)", ["dns.domain_expired"])
        if not db.execute("SELECT COUNT(*) FROM main_systemnotification WHERE name=%s",
                          ["dns.domain_expiration_warning"])[0][0]:
            db.execute("INSERT INTO main_systemnotification(name) VALUES(%s)", ["dns.domain_expiration_warning"])

    def backwards(self):
        pass
