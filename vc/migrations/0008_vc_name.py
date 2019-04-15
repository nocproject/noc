# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc name
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Python modules
import re
# Third-party modules
from south.db import db
from django.db import models

rx_underline = re.compile("\s+")
rx_empty = re.compile(r"[^a-zA-Z0-9\-_]+")


class Migration(object):
    def forwards(self):
        db.add_column("vc_vc", "name", models.CharField("Name", max_length=64, null=True, blank=True))
        names = {}  # vc_domain_id -> names
        for vc_id, vc_domain_id, l1, description in db.execute("SELECT id,vc_domain_id,l1,description FROM vc_vc"):
            if vc_domain_id not in names:
                names[vc_domain_id] = {}
            name = rx_underline.sub("_", description)
            name = rx_empty.sub("", name)
            if name in names[vc_domain_id]:
                name = "%s_%04d" % (name, l1)
            names[vc_domain_id][name] = None
            db.execute("UPDATE vc_vc SET name=%s WHERE id=%s", [name, vc_id])
        db.execute("COMMIT")
        db.execute("ALTER TABLE vc_vc ALTER COLUMN name SET NOT NULL")
        db.execute("ALTER TABLE vc_vc ALTER COLUMN description DROP NOT NULL")
        db.create_unique('vc_vc', ['vc_domain_id', 'name'])

    def backwards(self):
        pass
