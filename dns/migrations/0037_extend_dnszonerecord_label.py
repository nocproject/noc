# -*- coding: utf-8 -*-

from south.db import db

class Migration:
<<<<<<< HEAD

    def forwards(self):
        db.execute("ALTER TABLE dns_dnszonerecord ALTER name TYPE VARCHAR(64)")

=======
    
    def forwards(self):
        db.execute("ALTER TABLE dns_dnszonerecord ALTER name TYPE VARCHAR(64)")
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.execute("ALTER TABLE dns_dnszonerecord ALTER name TYPE VARCHAR(32)")
