# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Language model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
=======
##----------------------------------------------------------------------
## Language model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from django.db import models


class Language(models.Model):
    """
    Language
    """
    class Meta:
        app_label = "main"
        db_table = "main_language"
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        ordering = ["name"]

    name = models.CharField("Name", max_length=32, unique=True)
    native_name = models.CharField("Native Name", max_length=32)
    is_active = models.BooleanField("Is Active", default=False)

    def __unicode__(self):
        return self.name
