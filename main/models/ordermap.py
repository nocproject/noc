# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# OrderMap model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models


class OrderMap(models.Model):
    """
    Custom field description
    """
    class Meta:
        verbose_name = "Order Map"
        verbose_name_plural = "Order Map"
        db_table = "main_ordermap"
        app_label = "main"
        unique_together = [("scope", "scope_id")]

    scope = models.CharField("Scope", max_length=64)
    scope_id = models.CharField("ID", max_length=24)
    name = models.CharField("Name", max_length=256)

    def __unicode__(self):
        return "%s:%s" % (self.scope, self.id)
