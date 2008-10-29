from noc.cm.models import Object
import noc.sa.periodic

class Task(noc.sa.periodic.Task):
    name="cm.dns_pull"
    description=""
    
    def execute(self):
        Object.global_pull("dns")
        return True
        