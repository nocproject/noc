# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# dns.update_domain_expiration task
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## dns.update_domain_expiration task
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
import noc.lib.periodic
import datetime,re,logging

class Task(noc.lib.periodic.Task):
    name="dns.update_domain_expiration"
    description=""
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute(self):
        from noc.dns.models import DNSZone
        from noc.peer.whois import whois
        # Find all second-level domains
        for z in DNSZone.objects.filter(name__regex=r"^[^.]+\.[^.]+$"):
            r=whois(z.name,["paid-till"])
            if not r:
                continue
            l=r[0][1].replace("-",".").split(".")
            if len(l)!=3:
                continue
            year,month,day=[int(x) for x in l]
            try:
                paid_till=datetime.date(year=year,month=month,day=day)
            except ValueError:
                continue
            if z.paid_till!=paid_till: # Update paid-till when necessary
                logging.info("%s: Change %s's paid-till to %s"%(self.name,z.name,paid_till))
                z.paid_till=paid_till
                z.save()
        return True
