# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# FM module database models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel


@six.python_2_unicode_compatible
class IgnoreEventRules(NOCModel):
    class Meta(object):
        app_label = "fm"
        db_table = "fm_ignoreeventrules"
        verbose_name = "Ignore Event Rule"
        verbose_name_plural = "Ignore Event Rules"
        unique_together = [("left_re", "right_re")]

    name = models.CharField("Name", max_length=64, unique=True)
    left_re = models.CharField("Left RE", max_length=256)
    right_re = models.CharField("Right Re", max_length=256)
    is_active = models.BooleanField("Is Active", default=True)
    description = models.TextField("Description", null=True, blank=True)

    def __str__(self):
        return "%s (%s, %s)" % (self.name, self.left_re, self.right_re)
