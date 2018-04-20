# encoding: utf-8
import datetime
from south.db import db
from django.db import models

class Migration:

    def forwards(self):
        # VRFGroup
        db.delete_column("ip_vrfgroup","unique_addresses")
        # Delete obsolete tables
        db.delete_table("ip_ipv4block")
        db.delete_table("ip_ipv4address")
        db.delete_table("ip_ipv4blockaccess")
        db.delete_table("ip_ipv4blockbookmark")
        db.delete_table("ip_ipv4addressrange")
        db.execute("DROP FUNCTION free_ip(INTEGER,CIDR)")
<<<<<<< HEAD

    def backwards(self):
        pass

=======
    
    def backwards(self):
        pass
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

