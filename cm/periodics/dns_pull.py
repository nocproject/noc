from noc.cm.models import Object
import noc.main.periodic

class Task(noc.main.periodic.Task):
    name="cm.dns_pull"
    description=""
    
    def execute(self):
        Object.global_pull("dns")
        return True
        