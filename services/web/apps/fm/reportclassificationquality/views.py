# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Classification Quality Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.fm.models.eventclass import EventClass
from noc.fm.models.activeevent import ActiveEvent
from noc.core.translation import ugettext as _


class ReportClassificationQuality(SimpleReport):
    title = _("Classification Quality")

    def get_data(self, request, **kwargs):
        default_ids = [c.id for c in
                       EventClass.objects.filter(name__startswith="Unknown | ")]
        count = ActiveEvent.objects.count()
        not_classified = ActiveEvent.objects.filter(event_class__in=default_ids).count()
        classified = count - not_classified
        quality = classified * 100 / count if count else 100
        data = [
            ["Active Events", classified, count, quality],
        ]
        return self.from_dataset(title=self.title,
            columns=["",
                TableColumn("Classified", format="integer", align="right"),
                TableColumn("Total", format="integer", align="right"),
                TableColumn("Quality", format="percent", align="right")
                ],
            data=data)
