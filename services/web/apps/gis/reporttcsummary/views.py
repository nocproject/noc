# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## gis.reporttcsummary
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow, TableColumn
from noc.gis.models import Map, TileCache
from noc.gis.geo import MIN_ZOOM, MAX_ZOOM


class ReportTCSummaryApplication(SimpleReport):
    title = "TileCache Summary"

    def get_data(self, **kwargs):
        data = []
        for m in Map.objects.filter(is_active=True).order_by("name"):
            data += [SectionRow(m.name)]
            for zoom in range(MIN_ZOOM, MAX_ZOOM + 1):
                tcc = TileCache.objects.filter(map=m.id, zoom=zoom).count()
                mt = 2 ** (2 * zoom)
                data += [[zoom, tcc, mt, tcc * 100.0 / mt]]
        return self.from_dataset(title=self.title,
                                 columns=[
                                     TableColumn("Zoom", align="right"),
                                     TableColumn("Tiles", align="right",
                                                 format="integer"),
                                     TableColumn("Max. Tiles", align="right",
                                                 format="integer"),
                                     TableColumn("%", align="right",
                                                 format="percent")],
                                 data=data)
