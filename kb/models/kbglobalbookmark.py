# ---------------------------------------------------------------------
# KBGlobalBookmark
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db.models.base import Model
from django.db import models

# NOC modules
from noc.kb.models.kbentry import KBEntry
from noc.core.comp import smart_text


class KBGlobalBookmark(Model):
    """
    Global Bookmarks
    @todo: Replace with boolean flag in KBEntry
    """

    class Meta(object):
        verbose_name = "KB Global Bookmark"
        verbose_name_plural = "KB Global Bookmarks"
        app_label = "kb"
        db_table = "kb_kbglobalbookmark"

    kb_entry = models.ForeignKey(
        KBEntry, verbose_name="KBEntry", unique=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return smart_text(self.kb_entry)
