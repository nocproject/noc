# ----------------------------------------------------------------------
# Move Event Class handlers to Event Disposition Rule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import uuid

# Third-party modules
from pymongo import InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration

interaction_map = {
    "log_cmd": 0,
    "log_login": 1,
    "log_logout": 2,
    "log_reboot": 3,
    "log_started": 4,
    "log_halted": 5,
    "log_config_changed": 6,
    "on_system_start": 4,
    "on_config_change": 6,
}
discovery_funcs = {"on_system_start", "on_config_change", "schedule_discovery"}


class Migration(BaseMigration):

    def migrate(self):
        bulk = []
        for ec in self.mongo_db["noc.eventclasses"].find():
            if not ec.get("disposition") or not ec.get("handlers"):
                continue
            for d in ec["disposition"] or []:
                r = {
                    "name": f"{ec['name']} - {d['name']}",
                    "uuid": uuid.uuid4(),
                    "is_active": True,
                    "combo_condition": d["combo_condition"],
                    "combo_window": d.get("combo_window") or 0,
                    "combo_count": d.get("combo_count") or 0,
                    "alarm_disposition": d["alarm_class"],
                    "default_action": {"raise": "R", "clear": "C", "ignore": "I"}[d["action"]],
                    "conditions": [{"event_class_re": ec["name"]}],
                }
                interaction, discovery = None, False
                for h in ec.get("handlers") or []:
                    _, function = h.rsplit(".", 1)
                    if function in interaction_map:
                        interaction = interaction_map[function]
                    if function in discovery_funcs:
                        discovery = True
                if interaction is not None or discovery:
                    r["object_actions"] = {
                        "interaction_audit": interaction,
                        "run_discovery": discovery,
                    }
                bulk += [InsertOne(r)]
        coll = self.mongo_db["dispositionrules"]
        if bulk:
            coll.bulk_write(bulk)
