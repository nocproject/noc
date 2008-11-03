from noc.main.report import Column
import noc.main.report

class Report(noc.main.report.Report):
    name="dns.missed_p2p_addresses"
    title="/30 allocations without ip addresses"
    requires_cursor=True
    columns=[Column("Prefix")]
    
    def get_queryset(self):
        vrf_id=self.execute("SELECT id FROM ip_vrf WHERE rd='0:0'")[0][0]
        return self.execute("""
            SELECT prefix
            FROM ip_ipv4block b
            WHERE masklen(prefix)=30
                AND vrf_id=%s
                AND (SELECT COUNT(*) FROM ip_ipv4address WHERE vrf_id=%s AND ip<<b.prefix)=0
            ORDER BY prefix""",[vrf_id,vrf_id])