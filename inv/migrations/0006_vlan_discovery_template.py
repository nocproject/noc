# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Initialize vlan discovery template
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from south.db import db


NEW_VLANS_REPORT_SUBJECT = "{{ count }} new VLANs discovered"
NEW_VLANS_REPORT_BODY = """{{ count }} new VLANs discovered

{% for p in vcs %}{{p.vc_domain.name}}: VLAN {{p.l1}} ({{p.name}})
{% endfor %}
"""


class Migration:
    depends_on = [
        ("main", "0037_template")
    ]

    def forwards(self):
        for tn, description, subject, body in [
            (
                "inv.discovery.new_vlans_report",
                "Discovery's New VLANs Report",
                NEW_VLANS_REPORT_SUBJECT,
                NEW_VLANS_REPORT_BODY
            )]:
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
        for tn in ["inv.discovery.new_vlans_report"]:
            tid = db.execute("SELECT id FROM main_template WHERE name=%s",
                [tn])[0][0]
            db.execute("DELETE FROM main_systemtemplate WHERE template_id=%s", [tid])
            db.execute("DELETE FROM main_template WHERE id=%s", [tid])
