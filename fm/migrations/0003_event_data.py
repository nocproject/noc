from south.db import db
from noc.fm.models import *

EVENT_PRIORITY=[
    (0,    "DEFAULT",  "Unclassified event"),
    (0,    "INFO",     "Informational message"),
    (1000, "NORMAL",   "Normal event. No services affected"),
    (2000, "WARNING",  "Some network services can possible be affected"),
    (3000, "MINOR",    "Single service can be affected"),
    (4000, "MAJOR",    "Some part of network services affected"),
    (5000, "CRITICAL", "Serious part of network services affected"),
]

EVENT_CLASS=[
    ("DEFAULT",  "Unclassified"),
    ("SYSTEM",   "System Event"),
    ("NETWORK",  "Network Event"),
    ("SECURITY", "Security Event"),
]

class Migration:
    
    def forwards(self):
        for priority,name,description in EVENT_PRIORITY:
            db.execute("INSERT INTO fm_eventpriority(name,priority,description) VALUES(%s,%s,%s)",[name,priority,description])
        for name,description in EVENT_CLASS:
            db.execute("INSERT INTO fm_eventclass(name,description) VALUES(%s,%s)",[name,description])
    
    def backwards(self):
        "Write your backwards migration here"
