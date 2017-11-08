# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# KBEntryPreviewLog
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.contrib.auth.models import User
from django.db import models
# NOC modules
from noc.kb.models.kbentry import KBEntry


class KBEntryPreviewLog(models.Model):
    """
    Preview Log
    """

    class Meta:
        verbose_name = "KB Entry Preview Log"
        verbose_name_plural = "KB Entry Preview Log"
        app_label = "kb"
        db_table = "kb_kbentrypreviewlog"

    kb_entry = models.ForeignKey(KBEntry, verbose_name="KB Entry")
    timestamp = models.DateTimeField("Timestamp", auto_now_add=True)
    user = models.ForeignKey(User, verbose_name="User")
