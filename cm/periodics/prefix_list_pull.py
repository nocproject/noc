import noc.sa.periodic

class Task(noc.sa.periodic.Task):
    name="cm.prefix_list_pull"
    description=""
    
    def execute(self):
        from noc.cm.models import PrefixList
        PrefixList.global_pull()
        return True
