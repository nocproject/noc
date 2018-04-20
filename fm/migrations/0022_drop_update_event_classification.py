
from south.db import db
<<<<<<< HEAD


class Migration:

    def forwards(self):
        db.execute("DROP FUNCTION update_event_classification(INTEGER,INTEGER,INTEGER,INTEGER,INTEGER,TEXT,TEXT,TEXT[][])")

=======
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.execute("DROP FUNCTION update_event_classification(INTEGER,INTEGER,INTEGER,INTEGER,INTEGER,TEXT,TEXT,TEXT[][])")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        "Write your backwards migration here"
