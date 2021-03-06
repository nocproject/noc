# ----------------------------------------------------------------------
# event data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration

EVENT_PRIORITY = [
    (0, "DEFAULT", "Unclassified event"),
    (0, "INFO", "Informational message"),
    (1000, "NORMAL", "Normal event. No services affected"),
    (2000, "WARNING", "Some network services can possible be affected"),
    (3000, "MINOR", "Single service can be affected"),
    (4000, "MAJOR", "Some part of network services affected"),
    (5000, "CRITICAL", "Serious part of network services affected"),
]

EVENT_CATEGORY = [
    ("DEFAULT", "Unclassified"),
    ("SYSTEM", "System Event"),
    ("NETWORK", "Network Event"),
    ("SECURITY", "Security Event"),
    ("SERVICE", "Service Event"),
]


class Migration(BaseMigration):
    def migrate(self):
        for priority, name, description in EVENT_PRIORITY:
            self.db.execute(
                "INSERT INTO fm_eventpriority(name,priority,description) VALUES(%s,%s,%s)",
                [name, priority, description],
            )
        for name, description in EVENT_CATEGORY:
            self.db.execute(
                "INSERT INTO fm_eventcategory(name,description) VALUES(%s,%s)", [name, description]
            )
        default_priority_id = self.db.execute(
            "SELECT id FROM fm_eventpriority WHERE NAME=%s", ["DEFAULT"]
        )[0][0]
        default_category_id = self.db.execute(
            "SELECT id FROM fm_eventcategory WHERE NAME=%s", ["DEFAULT"]
        )[0][0]
        self.db.execute(
            """INSERT INTO fm_eventclass(name,category_id,default_priority_id,variables,subject_template,body_template,
            last_modified) VALUES('DEFAULT',%s,%s,'','Unclassified event','Unclassified event','now')""",
            [default_category_id, default_priority_id],
        )
