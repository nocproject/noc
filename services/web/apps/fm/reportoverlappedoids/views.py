# ---------------------------------------------------------------------
# fm.reportoverlappedoids
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.simplereport import SimpleReport
from noc.fm.models.mib import MIBData
from noc.core.translation import ugettext as _


class ReportOverlappedOIDsApplication(SimpleReport):
    title = _("Overlapped MIB OIDs")

    def get_data(self, **kwargs):
        data = [
            (o.oid, o.name, ", ".join(o.aliases)) for o in MIBData.objects.filter(aliases__ne=[])
        ]
        return self.from_dataset(
            title=self.title, columns=["OID", "Chosen Name", "Aliases"], data=data, enumerate=True
        )
