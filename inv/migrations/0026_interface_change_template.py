# ---------------------------------------------------------------------
# Initialize interface status change Template
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


NEW_PREFIXES_REPORT_SUBJECT = (
    "[{{managed_object.name}}] Interface {{name}}({{description}})"
    ' is {% if status %}"up"{% else %}"down" {% endif %}'
)
NEW_PREFIXES_REPORT_BODY = (
    """Interface {{name}} ({{description}}) is {% if status %}"up"{% else %}"down" {% endif %}"""
)


class Migration(BaseMigration):
    depends_on = [("main", "0037_template")]

    def migrate(self):
        self.db.execute(
            "INSERT INTO main_template(name, subject, body) VALUES(%s, %s, %s)",
            [
                "inv.discovery.interface_status_change",
                NEW_PREFIXES_REPORT_SUBJECT,
                NEW_PREFIXES_REPORT_BODY,
            ],
        )
        self.db.execute(
            """
            INSERT INTO main_systemtemplate(name, description, template_id)
            SELECT %s, %s, id
            FROM main_template
            WHERE name=%s
        """,
            [
                "interface_status_change",
                "Interface status change notification",
                "inv.discovery.interface_status_change",
            ],
        )
