# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# CustomFieldEnumValue model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from .customfieldenumgroup import CustomFieldEnumGroup


@six.python_2_unicode_compatible
class CustomFieldEnumValue(NOCModel):
    """
    Enumeration groups values
    """

    class Meta(object):
        verbose_name = "Enum Group Value"
        verbose_name_plural = "Enum Group Values"
        db_table = "main_customfieldenumvalue"
        app_label = "main"
        unique_together = [("enum_group", "key")]

    enum_group = models.ForeignKey(
        CustomFieldEnumGroup,
        verbose_name="Enum Group",
        related_name="enumvalue_set",
        on_delete=models.CASCADE,
    )
    is_active = models.BooleanField("Is Active", default=True)
    key = models.CharField("Key", max_length=256)
    value = models.CharField("Value", max_length=256)

    def __str__(self):
        return "%s@%s:%s" % (self.enum_group.name, self.key, self.value)
