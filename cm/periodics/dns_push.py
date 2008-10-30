import noc.sa.periodic

class Task(noc.sa.periodic.Task):
    name="cm.dns_push"
    description=""
    
    def execute(self):
        from noc.cm.models import DNS
        DNS.global_push()
        return True

