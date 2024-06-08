# ----------------------------------------------------------------------
# Migrate Alarm Rules int Severities to AlarmSeverity
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateMany

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        s_coll = self.mongo_db["noc.alarmseverities"]
        s_label_map, severity_map = {}, {}
        default_severity = None
        for row in s_coll.find():
            s_label_map[f"noc::severity::{row['name'].lower()}"] = row["_id"]
            severity_map[row["severity"]] = row["_id"]
            if not default_severity:
                default_severity = row["_id"]
        bulk = []
        for row in self.mongo_db["alarmrules"].find({"actions.severity": {"$exists": True}}):
            actions = []
            severity = None
            for m in row["match"]:
                if "labels" not in m:
                    continue
                for ll in m["labels"]:
                    if ll in s_label_map:
                        severity = s_label_map[ll]
                        break
            for a in row["actions"]:
                if severity and "severity" in a:
                    a["severity"] = severity
                elif not severity and "severity" in a and severity + 1001 in severity_map:
                    a[severity + 1001] = severity_map[severity + 1001]
                if not severity and "severity" in a:
                    # Not detected severity
                    a["severity"] = default_severity
                actions.append(a)
            bulk.append(UpdateMany({"_id": row["_id"]}, {"$set": {"actions": actions}}))
        if bulk:
            self.mongo_db["alarmrules"].bulk_write(bulk)
