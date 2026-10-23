# ---------------------------------------------------------------------
# KBUserBookmark
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.aaa.models.user import User
from noc.kb.models.kbentry import KBEntry


class KBUserBookmark(NOCModel):
    """
    User Bookmarks
    """

    class Meta:
        verbose_name = "KB User Bookmark"
        verbose_name_plural = "KB User Bookmarks"
        app_label = "kb"
        db_table = "kb_kbuserbookmark"
        unique_together = [("user", "kb_entry")]

    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    kb_entry = models.ForeignKey(KBEntry, verbose_name="KBEntry", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user}: {self.kb_entry}"
