# -*- coding: utf-8 -*-

from south.db import db

class Migration:
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def forwards(self):
        db.delete_column("ip_ipv4block","modified_by_id")
        db.delete_column("ip_ipv4block","last_modified")
        db.delete_column("ip_ipv4address","modified_by_id")
        db.delete_column("ip_ipv4address","last_modified")
<<<<<<< HEAD

=======
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        pass
