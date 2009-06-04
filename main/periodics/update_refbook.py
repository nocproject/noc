# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Perform RefBook download
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic
from django.db.models import Q
import datetime

class Task(noc.sa.periodic.Task):
    name="main.update_refbook"
    description=""
    
    def execute(self):
        from noc.main.models import RefBook
        
        q=Q(next_update__isnull=True)|Q(next_update__lte=datetime.datetime.now())
        for rb in RefBook.objects.filter(is_enabled=True,downloader__isnull=False,refresh_interval__gt=0).filter(q):
            rb.download()
        return True
