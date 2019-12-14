# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# GroupAccess model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from noc.core.translation import ugettext as _
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.aaa.models.group import Group
from .managedobjectselector import ManagedObjectSelector
from .administrativedomain import AdministrativeDomain


@six.python_2_unicode_compatible
class GroupAccess(NOCModel):
    class Meta(object):
        verbose_name = _("Group Access")
        verbose_name_plural = _("Group Access")
        db_table = "sa_groupaccess"
        app_label = "sa"
        ordering = ["group"]

    group = models.ForeignKey(Group, verbose_name=_("Group"), on_delete=models.CASCADE)
    selector = models.ForeignKey(
        ManagedObjectSelector, null=True, blank=True, on_delete=models.CASCADE
    )
    administrative_domain = models.ForeignKey(
        AdministrativeDomain, null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        r = ["group=%s" % self.group.name]
        if self.selector:
            r += ["selector=%s" % self.selector.name]
        if self.administrative_domain:
            r += ["domain=%s" % self.administrative_domain.name]
        return "(%s)" % ", ".join(r)
