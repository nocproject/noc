# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic
from django.db.models import Q
import datetime,logging

class Task(noc.sa.periodic.Task):
    name="cm.config_pull"
    description=""
    
    def execute(self):
        from noc.cm.models import Config
        for o in Config.objects.filter((Q(next_pull__lt=datetime.datetime.now())|Q(next_pull__isnull=True))&Q(pull_every__isnull=False)).order_by("next_pull"):
            if o.managed_object.is_managed and o.managed_object.is_configuration_managed:
                logging.debug("Pulling %s",str(o))
                o.pull(self.sae)
        return True

