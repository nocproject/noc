# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Collector
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models


class Collector(models.Model):
    """
    Event collector
    """
    class Meta:
        verbose_name = "Collector"
        verbose_name_plural = "Collectors"
        db_table = "sa_collector"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    is_active = models.BooleanField("Is Active", default=True)
    description = models.TextField("Description", null=True, blank=True)

    def __unicode__(self):
        return self.name
