# ----------------------------------------------------------------------
# alarm reference
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        def process_event(event_id, alarm_id):
            e = None
            for c in (active_events, archived_events):
                e = c.find_one(event_id)
                if e:
                    break
            if not e:
                return
            assert e["_id"] == event_id
            alarms = e.get("alarms", [])
            if alarm_id not in alarms:
                alarms += [alarm_id]
                e["alarms"] = alarms
                c.save(e)

        def process_alarm(collection, doc):
            if "events" not in doc:
                return
            a_id = doc["_id"]
            for e_id in doc["events"]:
                process_event(e_id, a_id)
            del doc["events"]
            collection.save(doc)

        db = self.mongo_db
        active_alarms = db.noc.alarms.active
        archived_alarms = db.noc.alarms.archive
        active_events = db.noc.events.active
        archived_events = db.noc.events.archive

        for ac in (active_alarms, archived_alarms):
            for doc in ac.find():
                process_alarm(ac, doc)
