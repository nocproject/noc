from noc.main.report import Column
import noc.main.report
from noc.dns.generators import generator_registry

class Report(noc.main.report.Report):
    name="dns.supported_servers"
    title="Supported nameservers"
    requires_cursor=False
    columns=[Column("Type")]
    
    def get_queryset(self):
        r=[x[0] for x in generator_registry.choices]
        r.sort()
        return [(x,) for x in r]