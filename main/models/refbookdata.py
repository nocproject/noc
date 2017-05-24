# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# RefBookData
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from refbook import RefBook
from noc.core.model.fields import TextArrayField


class RBDManader(models.Manager):
    """
    Ref Book Data Manager
    """
    # Order by first field
    def get_query_set(self):
        return super(RBDManader, self).get_query_set().extra(order_by=["main_refbookdata.value[1]"])


class RefBookData(models.Model):
    """
    Ref. Book Data
    """
    class Meta:
        verbose_name = "Ref Book Data"
        verbose_name_plural = "Ref Book Data"

    ref_book = models.ForeignKey(RefBook, verbose_name="Ref Book")
    value = TextArrayField("Value")

    objects = RBDManader()

    def __unicode__(self):
        return u"%s: %s" % (self.ref_book, self.value)

    @property
    def items(self):
        """
        Returns list of pairs (field,data)
        """
        return zip(self.ref_book.fields, self.value)
