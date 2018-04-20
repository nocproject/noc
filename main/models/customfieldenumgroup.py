# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# CustomFieldEnumGroup model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
=======
##----------------------------------------------------------------------
## CustomFieldEnumGroup model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from django.db import models


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
<<<<<<< HEAD
        return self.name
=======
        return self.name
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
