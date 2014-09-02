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
;;
"""

class ZoneFile(object):
    TABSTOP = 8

    def __init__(self, zone, records):
        """
        :param zone: Zone name
        :param records: List of tuples (fqdn, type, content, ttl, prio).
            First record must be SOA
        :return:
        """
        if not records:
            raise ValueError("Zone must contain SOA record")
        if records[0][1] != "SOA":
            raise ValueError("First record must be SOA")
        self.zone = zone
        self.records = records

    def get_text(self):
        (primary, contact, serial,
         refresh, retry, expire, ttl) = self.records[0][2].split()
        serial = int(serial)
        refresh = int(refresh)
        retry = int(retry)
        expire = int(expire)
        ttl = int(ttl)
        if "@" in contact:
            contact = contact.replace("@", ".")
        if not contact.endswith("."):
            contact += "."

        suffix = self.zone + "."
        nsuffix = "." + suffix
        lnsuffix = len(nsuffix)
        # SOA
        z = [HEADER, """$ORIGIN %(domain)s.
$TTL %(ttl)d
@ IN SOA %(primary)s %(contact)s (
    %(serial)d ; serial
    %(refresh)d       ; refresh (%(pretty_refresh)s)
    %(retry)d        ; retry (%(pretty_retry)s)
    %(expire)d      ; expire (%(pretty_expire)s)
    %(ttl)d       ; minimum (%(pretty_ttl)s)
    )""" % {
            "domain": self.zone,
            "primary": primary,
            "contact": contact,
            "serial": serial,
            "ttl": ttl,
            "pretty_ttl": self.pretty_time(ttl),
            "refresh": refresh,
            "pretty_refresh": self.pretty_time(refresh),
            "retry": retry,
            "pretty_retry": self.pretty_time(retry),
            "expire": expire,
            "pretty_expire": self.pretty_time(expire),
        }]
        # Add records
        nses = []
        rr = []
        for name, type, content, ttl, prio in self.records[1:]:
            if not name.endswith(nsuffix) and name != suffix:
                continue  # Trash
            name = name[:-lnsuffix]  # Strip domain from name
            if type == "CNAME" and content.endswith(nsuffix):
                # Strip domain from content
                content = content[:-lnsuffix]
            if prio:
                content = "%s %s" % (prio, content)
            if not name and type == "NS":
                nses += [(name, type, content)]
            else:
                rr += [(name, type, content)]
        # prepare mask for 3-column format
        if rr:
            l1 = max(len(r[0]) for r in rr)
            l2 = max(len(r[1]) for r in rr)
            # Ceil to boundary of 4
            l1 = (l1 // self.TABSTOP + 1) * self.TABSTOP
            l2 = (l2 // self.TABSTOP + 1) * self.TABSTOP
        else:
            l1 = self.TABSTOP
            l2 = self.TABSTOP
        mask = "%%-%ds%%-%ds%%s" % (l1, l2)
        # Add zone NS
        if nses:
           z += [mask % tuple(r) for r in nses]
        # Add RRs
        if rr:
            # Format according to mask
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
            rr = t // w
            t -= rr * w
            r += [rr]
        z = []
        for rr, t in zip(r, T):
            if rr > 1:
                z += ["%d %ss" % (rr, t)]
            elif rr > 0:
                z += ["%d %s" % (rr, t)]
        return " ".join(z)
