# encoding: utf-8
import datetime
from south.db import db

class Migration:
    def forwards(self):
        db.execute("ALTER TABLE sa_managedobject ALTER remote_path TYPE VARCHAR(256)")
<<<<<<< HEAD

    def backwards(self):
        db.execute("ALTER TABLE sa_managedobject ALTER remote_path TYPE VARCHAR(32)")

=======
    
    def backwards(self):
        db.execute("ALTER TABLE sa_managedobject ALTER remote_path TYPE VARCHAR(32)")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
