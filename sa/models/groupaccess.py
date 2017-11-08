# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# GroupAccess model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

from django.contrib.auth.models import Group
from django.db import models
# Third-party modules
from django.utils.translation import ugettext_lazy as _

from .administrativedomain import AdministrativeDomain
# NOC modules
from .managedobjectselector import ManagedObjectSelector


class GroupAccess(models.Model):
    class Meta:
        verbose_name = _("Group Access")
        verbose_name_plural = _("Group Access")
        db_table = "sa_groupaccess"
        app_label = "sa"
        ordering = ["group"]

    group = models.ForeignKey(Group, verbose_name=_("Group"))
    selector = models.ForeignKey(ManagedObjectSelector,
                                 null=True, blank=True)
    administrative_domain = models.ForeignKey(
        AdministrativeDomain,
        null=True, blank=True
    )

    def __unicode__(self):
        r = [u"group=%s" % self.group.name]
        if self.selector:
            r += [u"selector=%s" % self.selector.name]
        if self.administrative_domain:
            r += [u"domain=%s" % self.administrative_domain.name]
        return u"(%s)" % u", ".join(r)
