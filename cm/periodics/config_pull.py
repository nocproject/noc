from noc.cm.models import Object
import noc.main.periodic
from django.db.models import Q
import datetime,logging

class Task(noc.main.periodic.Task):
    name="cm.config_pull"
    description=""
    
    def execute(self):
        for o in Object.objects.filter(handler_class_name="config",next_pull__lt=datetime.datetime.now()):
            logging.debug("Pulling %s",str(o))
            o.pull()
            now=datetime.datetime.now()
            o.last_pull=now
            o.next_pull=now+datetime.timedelta(seconds=o.pull_every)
            o.save()
        return True

