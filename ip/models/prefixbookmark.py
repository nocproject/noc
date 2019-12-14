# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PrefixBookmark model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from operator import attrgetter

# Third-party modules
import six
from noc.core.translation import ugettext as _
from django.db import models
from django.db.models import Q

# NOC modules
from noc.core.model.base import NOCModel
from noc.aaa.models.user import User
from .prefix import Prefix


@six.python_2_unicode_compatible
class PrefixBookmark(NOCModel):
    """
    User Bookmarks
    """

    class Meta(object):
        verbose_name = _("Prefix Bookmark")
        verbose_name_plural = _("Prefix Bookmarks")
        db_table = "ip_prefixbookmark"
        app_label = "ip"
        unique_together = [("user", "prefix")]

    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    prefix = models.ForeignKey(Prefix, verbose_name="Prefix", on_delete=models.CASCADE)

    def __str__(self):
        return "Bookmark at %s for %s" % (self.prefix, self.user.username)

    @classmethod
    def user_bookmarks(cls, user, vrf=None, afi=None):
        """
        Returns a prefixes bookmarked by user
        :param cls:
        :param user:
        :param vrf:
        :param afi:
        :return:
        """
        q = Q(user=user)
        if vrf:
            if afi:
                q &= Q(prefix__vrf=vrf, prefix__afi=afi)
            else:
                q &= Q(prefix__vrf=vrf)
        return sorted([b.prefix for b in cls.objects.filter(q)], key=attrgetter("prefix"))
