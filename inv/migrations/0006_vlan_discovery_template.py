# ---------------------------------------------------------------------
# Initialize vlan discovery template
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration

NEW_VLANS_REPORT_SUBJECT = "{{ count }} new VLANs discovered"
NEW_VLANS_REPORT_BODY = """{{ count }} new VLANs discovered

{% for p in vcs %}{{p.vc_domain.name}}: VLAN {{p.l1}} ({{p.name}})
{% endfor %}
"""


class Migration(BaseMigration):
    depends_on = [("main", "0037_template")]

    def migrate(self):
        for tn, description, subject, body in [
            (
                "inv.discovery.new_vlans_report",
                "Discovery's New VLANs Report",
                NEW_VLANS_REPORT_SUBJECT,
                NEW_VLANS_REPORT_BODY,
            )
        ]:
            self.db.execute(
                "INSERT INTO main_template(name, subject, body) VALUES(%s, %s, %s)",
                [tn, subject, body],
            )
            self.db.execute(
                """
                INSERT INTO main_systemtemplate(name, description, template_id)
                SELECT %s, %s, id
                FROM main_template
                WHERE name=%s
            """,
                [tn, description, tn],
            )
