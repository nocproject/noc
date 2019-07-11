# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VCType model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from django.db import models

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.model.base import NOCModel


@on_delete_check(check=[("vc.VCDomain", "type")])
@six.python_2_unicode_compatible
class VCType(NOCModel):
    """
    VC Type
    """

    class Meta(object):
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

    def __str__(self):
        return self.name
