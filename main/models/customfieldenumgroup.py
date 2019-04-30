# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# CustomFieldEnumGroup model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.model.decorator import on_delete_check


@on_delete_check(check=[
    ("main.CustomField", "enum_group"),
    ("main.CustomFieldEnumValue", "enum_group")
])
class CustomFieldEnumGroup(models.Model):
    """
    Enumeration groups for custom fields
    """
    class Meta:
        verbose_name = "Enum Group"
        verbose_name_plural = "Enum Groups"
        db_table = "main_customfieldenumgroup"
        app_label = "main"

    name = models.CharField("Name", max_length=128, unique=True)
    is_active = models.BooleanField("Is Active", default=True)
    description = models.TextField("Description", null=True, blank=True)

    def __unicode__(self):
        return self.name
