
from south.db import db
<<<<<<< HEAD


class Migration:

=======
from noc.fm.models import *

class Migration:
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def forwards(self):
        db.execute("UPDATE fm_event SET status='U' WHERE subject IS NULL")
        db.execute("UPDATE fm_event SET status='C' WHERE subject IS NOT NULL AND \"timestamp\"<('now'::timestamp-'1day'::interval)")
        db.execute("UPDATE fm_event SET status='A' WHERE subject IS NOT NULL AND \"timestamp\">=('now'::timestamp-'1day'::interval)")
<<<<<<< HEAD

=======
            
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        "Write your backwards migration here"
