# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BRASGroup
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models


class TerminationGroup(models.Model):
    """
    Termination Group
    """
    class Meta:
        verbose_name = "Termination Group"
        verbose_name_plural = "Termination Groups"
        db_table = "sa_terminationgroup"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", null=True, blank=True)
    # Dynamic pools oversubscription, in persent
    # 0 - no oversub
    # 10 -- 10% oversubscription
    # -10  -- Reserve 10%
    # dynamic_oversub = models.IntegerField("Dynamic Oversub", default=0)

    def __unicode__(self):
        return self.name
