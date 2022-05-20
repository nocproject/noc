# ---------------------------------------------------------------------
# KBUserBookmark
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db.models.base import Model
from django.db import models

# NOC modules
from noc.aaa.models.user import User
from noc.kb.models.kbentry import KBEntry
from noc.core.comp import smart_text


class KBUserBookmark(Model):
    """
    User Bookmarks
    """

    class Meta(object):
        verbose_name = "KB User Bookmark"
        verbose_name_plural = "KB User Bookmarks"
        app_label = "kb"
        db_table = "kb_kbuserbookmark"
        unique_together = [("user", "kb_entry")]

    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    kb_entry = models.ForeignKey(KBEntry, verbose_name="KBEntry", on_delete=models.CASCADE)

    def __str__(self):
        return "%s: %s" % (smart_text(self.user), smart_text(self.kb_entry))
