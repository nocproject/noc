# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# dns.check_domain_expiration task
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## dns.check_domain_expiration task
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
import noc.lib.periodic
from noc.settings import config
from django.utils.dateformat import DateFormat
import datetime

class Task(noc.lib.periodic.Task):
    name="dns.check_domain_expiration"
    description=""
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute(self):
        def format_table(l):
            mw=max([len(n) for n,d in l])
            m="%%%ds | %%s"%mw
            out=[m%("Domain","Expiration date")]
            for n,d in l:
                out+=[m%(n,DateFormat(d).format(date_format))]
            return "\n".join(out)
        #
        from noc.main.models import SystemNotification
        from noc.dns.models import DNSZone
<<<<<<< HEAD

=======
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        date_format=config.get("main","date_format")
        now=datetime.date.today()
        ## Check expired soon domains
        days=config.getint("dns","warn_before_expired_days")
        soon_expired=list([(z.name,z.paid_till)
            for z in DNSZone.objects.filter(paid_till__isnull=False,paid_till__range=[now+datetime.timedelta(days=1),now+datetime.timedelta(days=days)]).order_by("paid_till")])
        if soon_expired:
            SystemNotification.notify("dns.domain_expiration_warning",
                subject="%d domains to be expired in %d days"%(len(soon_expired),days),
                body="Following domains are to be expired in %d days:\n"%days+format_table(soon_expired)
                )
        ## Check expired domains
        expired=list([(z.name,z.paid_till)
            for z in DNSZone.objects.filter(paid_till__isnull=False,paid_till__lte=now).order_by("paid_till")])
        if expired:
            SystemNotification.notify("dns.domain_expired",
                subject="%d domains are expired"%(len(expired)),
                body="Following domains are expired:\n"+format_table(expired)
                )
        return True
