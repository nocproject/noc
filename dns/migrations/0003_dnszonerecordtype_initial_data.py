# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dnszonerecordtype data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function

# NOC modules
from noc.core.migration.base import BaseMigration

RECORD_TYPES = [
    ("A", True),
    ("AAAA", True),
    ("AFSDB", False),
    ("AXFR", False),
    ("CERT", False),
    ("CNAME", True),
    ("DHCID", False),
    ("DLV", False),
    ("DNAME", False),
    ("DNSKEY", False),
    ("DS", False),
    ("HIP", False),
    ("IPSECKEY", False),
    ("IXFR", False),
    ("KEY", False),
    ("LOC", False),
    ("MX", True),
    ("NAPTR", True),
    ("NS", True),
    ("NSEC", False),
    ("NSEC3", False),
    ("NSEC3PARAM", False),
    ("OPT", False),
    ("PTR", True),
    ("RRSIG", False),
    ("SIG", False),
    ("SPF", True),
    ("SRV", True),
    ("SSHFP", False),
    ("TA", False),
    ("TKEY", False),
    ("TSIG", False),
    ("TXT", True),
]


class Migration(BaseMigration):
    def migrate(self):
        rt = []
        for rtype, is_visible in RECORD_TYPES:
            if (
                self.db.execute(
                    "SELECT COUNT(*) FROM dns_dnszonerecordtype WHERE type=%s", [rtype]
                )[0][0]
                > 0
            ):
                continue
            rt += [(rtype, is_visible)]
        if rt:
            print("Creating DNS Zone record types: %s" % ", ".join(sorted([x[0] for x in rt])))
            for rtype, is_visible in rt:
                self.db.execute(
                    "INSERT INTO dns_dnszonerecordtype(type, is_visible) VALUES(%s, %s)",
                    [rtype, is_visible],
                )
