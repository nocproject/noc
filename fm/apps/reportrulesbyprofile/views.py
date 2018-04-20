# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Rules by Profile Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.sa.models import profile_registry
from noc.fm.models import EventClassificationRule


class Reportreportrulesbyprofile(SimpleReport):
    title = "Rules by Profile"

    def get_data(self,**kwargs):
        # profile -> (syslog, snmp, other)
        r = dict([(p, [0, 0, 0]) for p in profile_registry.classes])
        for rule in EventClassificationRule.objects.all():
            profile = None
            source = None
            for p in rule.patterns:
                if p.key_re in ("^profile$", "profile"):
                    profile = p.value_re
                elif p.key_re in ("^source$", "source"):
                    source = p.value_re
                if profile and source:
                    break
            for p in r:
                if not profile or re.search(profile, p):
                    d = r[p]
                    if source in ("syslog", "^syslog$"):
                        d[0] += 1
                    elif source in ("SNMP Trap", "^SNMP Trap$"):
                        d[1] += 1
                    else:
                        d[2] += 1
        # Build data
        data = [(p, v[0], v[1], v[2], v[0] + v[1] + v[2]) for p, v in r.items()]
        data = sorted(data, key=lambda x: -x[4])
        return self.from_dataset(title=self.title,
                                 columns=["Profile",
                                          TableColumn("Syslog", align="right",
                                                      format="integer",
                                                      total="sum"),
                                          TableColumn("SNMP Traps", align="right",
                                                      format="integer",
                                                      total="sum"),
                                          TableColumn("Other", align="right",
                                                      format="integer",
                                                      total="sum"),
                                          TableColumn("Total", align="right",
                                                      format="integer",
                                                      total="sum")],
                                 data=data)
