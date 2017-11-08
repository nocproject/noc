# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VCType model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models


class VCType(models.Model):
    """
    VC Type
    """

    class Meta:
        verbose_name = "VC Type"
        verbose_name_plural = "VC Types"
        db_table = "vc_vctype"
        app_label = "vc"

    name = models.CharField("Name", max_length=32, unique=True)
    min_labels = models.IntegerField("Min. Labels", default=1)
    label1_min = models.IntegerField("Label1 min")
    label1_max = models.IntegerField("Label1 max")
    label2_min = models.IntegerField("Label2 min", null=True, blank=True)
    label2_max = models.IntegerField("Label2 max", null=True, blank=True)

    def __unicode__(self):
        return self.name
