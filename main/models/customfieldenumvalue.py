# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# CustomFieldEnumValue model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from django.db import models
# NOC modules
from .customfieldenumgroup import CustomFieldEnumGroup
=======
##----------------------------------------------------------------------
## CustomFieldEnumValue model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## NOC modules
from customfieldenumgroup import CustomFieldEnumGroup
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class CustomFieldEnumValue(models.Model):
    """
    Enumeration groups values
    """
    class Meta:
        verbose_name = "Enum Group Value"
        verbose_name_plural = "Enum Group Values"
        db_table = "main_customfieldenumvalue"
        app_label = "main"
        unique_together = [("enum_group", "key")]

    enum_group = models.ForeignKey(
        CustomFieldEnumGroup,
        verbose_name="Enum Group",
<<<<<<< HEAD
        related_name="enumvalue_set"
    )
=======
        related_name="enumvalue_set")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    is_active = models.BooleanField("Is Active", default=True)
    key = models.CharField("Key", max_length=256)
    value = models.CharField("Value", max_length=256)

    def __unicode__(self):
        return u"%s@%s:%s" % (
            self.enum_group.name, self.key, self.value)
