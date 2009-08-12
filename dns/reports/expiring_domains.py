# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## dns.expiring_domains
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column,BooleanColumn
import noc.main.report
from noc.settings import config

class Report(noc.main.report.Report):
    name="dns.expiring_domains"
    title="Expiring domains"
    requires_cursor=True
    columns=[Column("Domain"),BooleanColumn("Expired"),Column("Paid Till")]
    
    def get_queryset(self):
        days=config.getint("dns","warn_before_expired_days")
        return self.execute("""SELECT name,paid_till<='now'::date,paid_till
            FROM dns_dnszone
            WHERE paid_till IS NOT NULL
                AND 'now'::date >= (paid_till-'%d days'::interval)
            ORDER BY paid_till"""%(days))
