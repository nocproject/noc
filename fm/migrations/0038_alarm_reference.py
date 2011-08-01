# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db
## NOC modules
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
        def process_event(event_id, alarm_id):
            c = active_events
            e = active_events.find_one(_id=event_id)
            if not e:
                e = archived_events.find_one(_id=event_id)
                c = archived_events
                if not e:
                    return
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
        
        db = get_db()
        active_alarms = db.noc.alarms.active
        archived_alarms = db.noc.alarms.archive
        active_events = db.noc.events.active
        archived_events = db.noc.events.archive
        
        for doc in active_alarms.find():
            process_alarm(active_alarms, doc)
        for doc in archived_alarms.find():
            process_alarm(archived_alarms, doc)
    
    def backwards(self):
        pass
