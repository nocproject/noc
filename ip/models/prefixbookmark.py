# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# PrefixBookmark model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from operator import attrgetter
# Django modules
=======
##----------------------------------------------------------------------
## PrefixBookmark model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from operator import attrgetter
## Django modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
<<<<<<< HEAD
# NOC modules
from .prefix import Prefix
=======
## NOC modules
from prefix import Prefix
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class PrefixBookmark(models.Model):
    """
    User Bookmarks
    """
    class Meta:
        verbose_name = _("Prefix Bookmark")
        verbose_name_plural = _("Prefix Bookmarks")
        db_table = "ip_prefixbookmark"
        app_label = "ip"
        unique_together = [("user", "prefix")]

    user = models.ForeignKey(User, verbose_name="User")
    prefix = models.ForeignKey(Prefix, verbose_name="Prefix")

    def __unicode__(self):
        return u"Bookmark at %s for %s" % (
            self.prefix, self.user.username)

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
        return sorted(
            [b.prefix for b in cls.objects.filter(q)],
            key=attrgetter("prefix")
        )
