# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db
# NOC modules
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.nosql import get_db


class Migration:
    def forwards(self):
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
<<<<<<< HEAD

=======
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        def process_alarm(collection, doc):
            if "events" not in doc:
                return
            a_id = doc["_id"]
            for e_id in doc["events"]:
                process_event(e_id, a_id)
            del doc["events"]
            collection.save(doc)
<<<<<<< HEAD

=======
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        db = get_db()
        active_alarms = db.noc.alarms.active
        archived_alarms = db.noc.alarms.archive
        active_events = db.noc.events.active
        archived_events = db.noc.events.archive
<<<<<<< HEAD

        for ac in (active_alarms, archived_alarms):
            for doc in ac.find():
                process_alarm(ac, doc)

=======
        
        for ac in (active_alarms, archived_alarms):
            for doc in ac.find():
                process_alarm(ac, doc)
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        pass
