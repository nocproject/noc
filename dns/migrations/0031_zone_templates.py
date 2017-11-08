# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Initialize discovery templates
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from south.db import db

NEW_ZONE_SUBJECT = "NOC: {{ name }} zone has been created"
NEW_ZONE_BODY = """New zone has been created: {{ name }}
===========[Zone Data]===========
{{ data }}
==========[End of Zone]==========
"""

ZONE_CHANGE_SUBJECT = "NOC: {{ name }} zone has been changed"
ZONE_CHANGE_BODY = """Zone has been changed: {{ name }}
=============[Diff]=============
{{ diff }}
==========[End of Diff]==========
"""


class Migration:
    depends_on = [
        ("main", "0037_template")
    ]

    def forwards(self):
        for tn, description, subject, body in [
            (
                    "dns.zone.new",
                    "New DNS zone",
                    NEW_ZONE_SUBJECT,
                    NEW_ZONE_BODY
            ),
            (
                    "dns.zone.change",
                    "DNS zone change",
                    ZONE_CHANGE_SUBJECT,
                    ZONE_CHANGE_BODY
            )
        ]:
            db.execute("INSERT INTO main_template(name, subject, body) VALUES(%s, %s, %s)", [
                tn, subject, body
            ])
            db.execute("""
                INSERT INTO main_systemtemplate(name, description, template_id)
                SELECT %s, %s, id
                FROM main_template
                WHERE name=%s
            """, [tn, description, tn])

    def backwards(self):
        for tn in ("dns.zone.new",
                   "dns.zone.change"):
            tid = db.execute("SELECT id FROM main_template WHERE name=%s",
                             [tn])[0][0]
            db.execute("DELETE FROM main_systemtemplate WHERE template_id=%s", [tid])
            db.execute("DELETE FROM main_template WHERE id=%s", [tid])
