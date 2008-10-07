from noc.main.report import Column
import noc.main.report

class Report(noc.main.report.Report):
    name="dns.missed_p2p_addresses"
    title="/30 allocations without ip addresses"
    requires_cursor=True
    columns=[Column("Prefix")]
    
    def get_queryset(self):
        vrf_id=self.execute("SELECT id FROM ip_vrf WHERE rd='0:0'")[0][0]
        return self.execute("SELECT prefix FROM ip_ipv4block WHERE masklen(prefix_cidr)=30 AND vrf_id=%s ORDER BY prefix_cidr",[vrf_id])