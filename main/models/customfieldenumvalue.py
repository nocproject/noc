# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# CustomFieldEnumValue model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# NOC modules
from customfieldenumgroup import CustomFieldEnumGroup


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
        related_name="enumvalue_set")
    is_active = models.BooleanField("Is Active", default=True)
    key = models.CharField("Key", max_length=256)
    value = models.CharField("Value", max_length=256)

    def __unicode__(self):
        return u"%s@%s:%s" % (
            self.enum_group.name, self.key, self.value)
