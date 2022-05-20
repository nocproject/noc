# ---------------------------------------------------------------------
# Language model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db.models.base import Model
from django.db import models

# NOC modules
from noc.core.model.decorator import on_delete_check


@on_delete_check(
    check=[
        ("main.RefBook", "language"),
        ("kb.KBEntry", "language"),
        ("kb.KBEntryTemplate", "language"),
    ]
)
class Language(Model):
    """
    Language
    """

    class Meta(object):
        app_label = "main"
        db_table = "main_language"
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        ordering = ["name"]

    name = models.CharField("Name", max_length=32, unique=True)
    native_name = models.CharField("Native Name", max_length=32)
    is_active = models.BooleanField("Is Active", default=False)

    def __str__(self):
        return self.name
