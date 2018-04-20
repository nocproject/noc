
from south.db import db
<<<<<<< HEAD
from django.db import models
=======
from noc.main.models import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

TIME_PATTERNS=[
    ("Any", "Always match", []),
    ("Workdays", "Match workdays", ["mon-fri"])
]

class Migration:
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def forwards(self):
        "Write your forwards migration here"
        for name,desc,tpd in TIME_PATTERNS:
            if db.execute("SELECT COUNT(*) FROM main_timepattern WHERE name=%s",[name])[0][0]==0:
                db.execute("INSERT INTO main_timepattern(name,description) VALUES(%s,%s)",[name,desc])
                tp_id=db.execute("SELECT id FROM main_timepattern WHERE name=%s",[name])[0][0]
                for tp in tpd:
                    db.execute("INSERT INTO main_timepatternterm(time_pattern_id,term) VALUES(%s,%s)",[tp_id,tp])
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        "Write your backwards migration here"
