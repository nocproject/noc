# ----------------------------------------------------------------------
# Move Event Class handlers to Event Disposition Rule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import uuid

# Third-party modules
import bson
from pymongo import InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.bi.decorator import bi_hash

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
        names = set()
        ac_map = {}
        for ac in self.mongo_db["noc.alarmclasses"].find({}, {"name": 1}):
            ac_map[ac["_id"]] = ac["name"]
        for ec in self.mongo_db["noc.eventclasses"].find():
            if not ec.get("disposition") and not ec.get("handlers"):
                continue
            disposition_names = []
            for d in ec["disposition"] or []:
                ac = d.get("alarm_class")
                if not ac:
                    continue
                elif disposition_names and d["name"] in disposition_names:
                    name = f"{ec['name']} ({ac_map.get(ac)},{d['name']}) ({disposition_names.index(d['name'])})"
                else:
                    name = f"{ec['name']} ({ac_map.get(ac)},{d['name']})"
                disposition_names.append(d["name"])
                if name in names:
                    continue
                r = {
                    "name": name,
                    "uuid": uuid.uuid4(),
                    "is_active": True,
                    "combo_condition": d["combo_condition"],
                    "combo_window": d.get("combo_window") or 0,
                    "combo_count": d.get("combo_count") or 0,
                    "alarm_disposition": d.get("alarm_class"),
                    "default_action": {"raise": "R", "clear": "C", "ignore": "I"}[d["action"]],
                    "conditions": [{"event_class_re": ec["name"]}],
                    "bi_id": bson.Int64(bi_hash(bson.ObjectId())),
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
                names.add(name)
            if ec["disposition"]:
                continue
            r = {
                "name": f"{ec['name']} (handlers)",
                "uuid": uuid.uuid4(),
                "is_active": True,
                "handlers": [],
                "conditions": [{"event_class_re": ec["name"]}],
                "bi_id": bson.Int64(bi_hash(bson.ObjectId())),
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
