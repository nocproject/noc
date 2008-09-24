##
## BINDv9 Zone Generator
##
from noc.dns.generators import BaseGenerator
import time

class Generator(BaseGenerator):
    def get_soa(self):
        nses=["\tNS\t%s\n"%n for n in self.zone.ns_list]
        nses="".join(nses)
        contact=self.zone.profile.zone_contact.replace("@",".")
        if not contact.endswith("."):
            contact+="."
        return """$ORIGIN .
$TTL %(ttl)d
%(domain)s IN SOA %(soa)s %(contact)s (
            %(serial)s ; serial
            %(refresh)d       ; refresh (%(pretty_refresh)s)
            %(retry)d        ; retry (%(pretty_retry)s)
            %(expire)d    ; expire (%(pretty_expire)s)
            %(ttl)d       ; minimum (%(pretty_ttl)s)
            )
%(nses)s
"""%{
            "domain"        : self.zone.name,
            "soa"           : self.zone.profile.zone_soa,
            "contact"       : contact,
            "serial"        : self.zone.serial,
            "ttl"           : self.zone.profile.zone_ttl,
            "pretty_ttl"    : self.pretty_time(self.zone.profile.zone_ttl),
            "refresh"       : self.zone.profile.zone_refresh,
            "pretty_refresh": self.pretty_time(self.zone.profile.zone_refresh),
            "retry"         : self.zone.profile.zone_retry,
            "pretty_retry"  : self.pretty_time(self.zone.profile.zone_retry),
            "expire"        : self.zone.profile.zone_expire,
            "pretty_expire" : self.pretty_time(self.zone.profile.zone_expire),
            "nses"          : nses
        }
        
    def get_records(self):
        s="$ORIGIN %s\n"%self.zone.name
        s+=self.format_3_columns(self.zone.records)
        return s
        
    def get_include(self,ns):
        T=time.localtime()
        s="""#
# WARNING: This is auto-generated file
# Do not edit manually
# Timestamp: %02d.%02d.%04d %02d:%02d:%02d
#
"""%(T[2],T[1],T[0],T[3],T[4],T[5])
        zones={}
        for p in ns.dnszoneprofile_set.filter():
            for z in p.dnszone_set.filter(is_auto_generated=True):
                zones[z.id]=z
        for z in zones.values():
            s+="""zone "%(zone)s" {
    type master;
    file "autozones/%(zone)s";
    allow-transfer { acl-backup-ns; };
};

"""%{"zone":z.name,"ns":ns.name}
        s+="""#
# End of auto-generated file
#
"""
        return s