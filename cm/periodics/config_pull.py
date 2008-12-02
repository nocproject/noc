import noc.sa.periodic
from django.db.models import Q
import datetime,logging

class Task(noc.sa.periodic.Task):
    name="cm.config_pull"
    description=""
    
    def execute(self):
        from noc.cm.models import Config
        for o in Config.objects.filter((Q(next_pull__lt=datetime.datetime.now())|Q(next_pull__isnull=True))&Q(pull_every__isnull=False)):
            logging.debug("Pulling %s",str(o))
            o.pull(self.sae)
        return True

