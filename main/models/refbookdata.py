# ---------------------------------------------------------------------
# RefBookData
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db.models.base import Model
from django.db import models

# NOC modules
from noc.core.model.fields import TextArrayField
from .refbook import RefBook


class RBDManader(models.Manager):
    """
    Ref Book Data Manager
    """

    # Order by first field
    def get_queryset(self):
        return super().get_queryset().extra(order_by=["main_refbookdata.value[1]"])


class RefBookData(Model):
    """
    Ref. Book Data
    """

    class Meta(object):
        app_label = "main"
        verbose_name = "Ref Book Data"
        verbose_name_plural = "Ref Book Data"

    ref_book = models.ForeignKey(RefBook, verbose_name="Ref Book", on_delete=models.CASCADE)
    value = TextArrayField("Value")

    objects = RBDManader()

    def __str__(self):
        return "%s: %s" % (self.ref_book, self.value)

    @property
    def items(self):
        """
        Returns list of pairs (field,data)
        """
        return list(zip(self.ref_book.fields, self.value))
