# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# KBEntryHistory model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.contrib.auth.models import User
from django.db import models
# NOC modules
from noc.kb.models.kbentry import KBEntry


class KBEntryHistory(models.Model):
    """
    Modification History
    """
    class Meta:
        verbose_name = "KB Entry History"
        verbose_name_plural = "KB Entry Histories"
        app_label = "kb"
        db_table = "kb_kbentryhistory"
        ordering = ("kb_entry", "timestamp")

    kb_entry = models.ForeignKey(KBEntry, verbose_name="KB Entry")
    timestamp = models.DateTimeField("Timestamp", auto_now_add=True)
    user = models.ForeignKey(User, verbose_name="User")
    diff = models.TextField("Diff")
