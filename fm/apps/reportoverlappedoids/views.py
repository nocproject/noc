# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.reportoverlappedoids
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.fm.models import MIBData


class ReportOverlappedOIDsApplication(SimpleReport):
    title = "Overlapped MIB OIDs"

    def get_data(self, **kwargs):
        data = [
            (o.oid, o.name, ", ".join(o.aliases))
            for o in MIBData.objects.filter(aliases__ne=[])
        ]
        return self.from_dataset(title=self.title,
                                 columns=["OID", "Chosen Name", "Aliases"],
                                 data=data,
                                 enumerate=True)
