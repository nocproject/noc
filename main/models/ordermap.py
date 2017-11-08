# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# OrderMap model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# model -> label field
ORDER_MAP_MODELS = {
    "sa.Profile": "name",
    "inv.Platform": "full_name",
    "inv.Firmware": "version"
}


class OrderMap(models.Model):
    """
    Custom field description
    """

    class Meta:
        verbose_name = "Order Map"
        verbose_name_plural = "Order Map"
        db_table = "main_ordermap"
        app_label = "main"
        unique_together = [("model", "ref_id")]

    model = models.CharField("Model", max_length=64)
    ref_id = models.CharField("ID", max_length=24)
    name = models.CharField("Name", max_length=256)

    def __unicode__(self):
        return "%s:%s" % (self.model, self.ref_id)

    @staticmethod
    def update_for_model(model):
        from django.db import connection
        from noc.models import get_model
        # Get model data
        name_field = ORDER_MAP_MODELS[model]
        coll = get_model(model)._get_collection()
        data = [
            (model, str(d["_id"]), d[name_field])
            for d in coll.find({}, {"_id": 1, name_field: 1})
        ]
        c = connection.cursor()
        c.execute("DELETE FROM main_ordermap WHERE model = %s", [model])
        c.execute("INSERT INTO main_ordermap(model, ref_id, name) VALUES " + ",".join(
            c.mogrify("(%s,%s,%s)", d) for d in data))

    @staticmethod
    def update_models():
        for m in ORDER_MAP_MODELS:
            OrderMap.update_for_model(m)
