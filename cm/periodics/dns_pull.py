import noc.sa.periodic

class Task(noc.sa.periodic.Task):
    name="cm.dns_pull"
    description=""
    
    def execute(self):
        from noc.cm.models import DNS
        DNS.global_pull()
        return True
        