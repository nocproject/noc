# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.reportobjectsummary
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel


class ReportObjectSummaryApplication(SimpleReport):
    title = "Object Summary"

    def get_data(self, **kwargs):
        self.model_name = {}  # oid -> name
        data = defaultdict(int)
        for c in Object._get_collection().find():
            n = self.get_model_name(c["model"])
            if n:
                data[n] += 1
        data = sorted(((k, data[k]) for k in data), key=lambda x: -x[1])
        return self.from_dataset(
            title=self.title,
            columns=[
                "Model",
                TableColumn("Count", format="numeric", align="right")
            ],
            data=data
        )

    def get_model_name(self, oid):
        try:
            return self.model_name[oid]
        except KeyError:
            n = ObjectModel.objects.filter(id=oid).first()
            if n:
                self.model_name[oid] = n.name
                return n.name
            else:
                self.model_name[oid] = None
                return None