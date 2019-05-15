# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# KBUserBookmark
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from django.contrib.auth.models import User
from django.db import models
# NOC modules
from noc.kb.models.kbentry import KBEntry


@six.python_2_unicode_compatible
class KBUserBookmark(models.Model):
    """
    User Bookmarks
    """
    class Meta(object):
        verbose_name = "KB User Bookmark"
        verbose_name_plural = "KB User Bookmarks"
        app_label = "kb"
        db_table = "kb_kbuserbookmark"
        unique_together = [("user", "kb_entry")]

    user = models.ForeignKey(User, verbose_name="User")
    kb_entry = models.ForeignKey(KBEntry, verbose_name="KBEntry")

    def __str__(self):
        return u"%s: %s" % (unicode(self.user), unicode(self.kb_entry))
