# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BIND-compatible zonefile generator
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

HEADER = """;;
;; WARNING: Auto-generated zone file
;; Do not edit manually
;;"""

FOOTER = """;;
;; End of auto-generated zone
;;"""

class ZoneFile(object):
    def __init__(self, zone, soa, contact, serial,
                 refresh, retry, expire, ttl, records):
        """
        :param zone: Zone name
        :param soa: SOA
        :param contact:
        :param serial:
        :param refresh:
        :param retry:
        :param expire:
        :param ttl:
        :param records: List of tuples (fqdn, type, content, ttl, prio)
        :return:
        """
        self.zone = zone
        self.soa = soa
        if "@" in contact:
            contact = contact.replace("@", ".")
        if not contact.endswith("."):
            contact += "."
        self.contact = contact
        self.serial = serial
        self.refresh = refresh
        self.retry = retry
        self.expire = expire
        self.ttl = ttl
        self.records = records

    def get_text(self):
        suffix = self.zone + "."
        nsuffix = "." + suffix
        lnsuffix = len(nsuffix)
        # SOA
        z = [HEADER, """
$ORIGIN %(domain)s
$TTL %(ttl)d
%(domain)s IN SOA %(soa)s %(contact)s (
    %(serial)s ; serial
    %(refresh)d       ; refresh (%(pretty_refresh)s)
    %(retry)d        ; retry (%(pretty_retry)s)
    %(expire)d      ; expire (%(pretty_expire)s)
    %(ttl)d       ; minimum (%(pretty_ttl)s)
    )""" % {
            "domain": self.zone,
            "soa": self.soa,
            "contact": self.contact,
            "serial": self.serial,
            "ttl": self.ttl,
            "pretty_ttl": self.pretty_time(self.ttl),
            "refresh": self.refresh,
            "pretty_refresh": self.pretty_time(self.refresh),
            "retry": self.retry,
            "pretty_retry": self.pretty_time(self.retry),
            "expire": self.expire,
            "pretty_expire": self.pretty_time(self.expire),
        }]
        # Add records
        rr = []
        for name, type, content, ttl, prio in self.records:
            if not name.endswith(nsuffix) and name != suffix:
                continue  # Trash
            name = name[:-lnsuffix]  # Strip domain from name
            if type == "CNAME" and content.endswith(nsuffix):
                # Strip domain from content
                content = content[:-lnsuffix]
            if prio is not None:
                content = "%s %s" % (prio, content)
            rr += [(name, type, content)]
        # Pretty format records to 3 columns
        if rr:
            l1 = max(len(r[0]) for r in rr)
            l2 = max(len(r[1]) for r in rr)
            # Ceil to boundary of 4
            l1 = (l1 // 4 + 1) * 4
            l2 = (l2 // 4 + 1) * 4
            # Format according to mask
            mask = "%%-%ds%%-%ds%%s" % (l1, l2)
            z += [mask % tuple(r) for r in rr]
        z += [FOOTER]
        return "\n".join(z)

    def pretty_time(self, t):
        """
        Format seconds to human-readable time for comments
        :param t:
        :return:
        """
        if not t:
            return "zero"
        T = ["week", "day", "hour", "min", "sec"]
        W = [345600, 86400, 3600, 60, 1]
        r = []
        for w in W:
            rr = int(t / w)
            t -= rr * w
            r += [rr]
        z = []
        for rr, t in zip(r, T):
            if rr > 1:
                z += ["%d %ss" % (rr, t)]
            elif rr > 0:
                z += ["%d %s" % (rr, t)]
        return " ".join(z)
