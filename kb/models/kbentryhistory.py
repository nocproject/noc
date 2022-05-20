# ---------------------------------------------------------------------
# KBEntryHistory model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db.models.base import Model
from django.db import models

# NOC modules
from noc.aaa.models.user import User
from noc.kb.models.kbentry import KBEntry


class KBEntryHistory(Model):
    """
    Modification History
    """

    class Meta(object):
        verbose_name = "KB Entry History"
        verbose_name_plural = "KB Entry Histories"
        app_label = "kb"
        db_table = "kb_kbentryhistory"
        ordering = ("kb_entry", "timestamp")

    kb_entry = models.ForeignKey(KBEntry, verbose_name="KB Entry", on_delete=models.CASCADE)
    timestamp = models.DateTimeField("Timestamp", auto_now_add=True)
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    diff = models.TextField("Diff")
