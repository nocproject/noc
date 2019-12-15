# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc name
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration

rx_underline = re.compile(r"\s+")
rx_empty = re.compile(r"[^a-zA-Z0-9\-_]+")


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "vc_vc", "name", models.CharField("Name", max_length=64, null=True, blank=True)
        )
        names = {}  # vc_domain_id -> names
        for vc_id, vc_domain_id, l1, description in self.db.execute(
            "SELECT id,vc_domain_id,l1,description FROM vc_vc"
        ):
            if vc_domain_id not in names:
                names[vc_domain_id] = {}
            name = rx_underline.sub("_", description)
            name = rx_empty.sub("", name)
            if name in names[vc_domain_id]:
                name = "%s_%04d" % (name, l1)
            names[vc_domain_id][name] = None
            self.db.execute("UPDATE vc_vc SET name=%s WHERE id=%s", [name, vc_id])
        self.db.execute("COMMIT")
        self.db.execute("ALTER TABLE vc_vc ALTER COLUMN name SET NOT NULL")
        self.db.execute("ALTER TABLE vc_vc ALTER COLUMN description DROP NOT NULL")
        self.db.create_index("vc_vc", ["vc_domain_id", "name"], unique=True)
