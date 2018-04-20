from south.db import db
from django.db import models

class Migration:
    def forwards(self):
        db.delete_column("sa_activator", "ip")
        db.delete_column("sa_activator", "to_ip")
        db.execute("ALTER TABLE sa_activator ALTER prefix_table_id SET NOT NULL")

    def backwards(self):
<<<<<<< HEAD
        pass
=======
        pass
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
