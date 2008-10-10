from noc.cm.models import Object
import noc.main.periodic

class Task(noc.main.periodic.Task):
    name="cm.prefix_list_pull"
    description=""
    
    def execute(self):
        Object.global_pull("prefix-list")
        return True
