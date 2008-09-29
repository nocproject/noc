from noc.main.report import BaseReport,Column

class Report(BaseReport):
    title="Zones at nameservers"
    requires_cursor=True
    columns=[Column("Nameserver"),Column("Zones",align="RIGHT")]
    
    def get_queryset(self):
        return self.execute("""SELECT ns.name,COUNT(*)
        FROM dns_dnsserver ns JOIN dns_dnszoneprofile_ns_servers nss ON (ns.id=nss.dnsserver_id) JOIN dns_dnszoneprofile p
            ON (nss.dnszoneprofile_id=p.id) JOIN dns_dnszone z ON (p.id=z.profile_id) GROUP BY 1 ORDER BY 2 DESC""")