# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column
import noc.main.report
from noc.lib.validators import is_ipv4
from noc.cm.models import Config

class Report(noc.main.report.Report):
    name="cm.ip_addresses_in_config"
    title="IP Addresses in Config"
    columns=[
            Column("Repo Path"),
            Column("IP Address")
            ]
    
    def get_queryset(self):
        return [(c.repo_path,c.managed_object.address) for c in Config.objects.all() if is_ipv4(c.managed_object.address)]
