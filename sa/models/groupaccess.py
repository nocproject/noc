# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# GroupAccess model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import Group
# NOC modules
from .managedobjectselector import ManagedObjectSelector
from .administrativedomain import AdministrativeDomain
=======
##----------------------------------------------------------------------
## GroupAccess model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import Group
## NOC modules
from managedobjectselector import ManagedObjectSelector
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class GroupAccess(models.Model):
    class Meta:
        verbose_name = _("Group Access")
        verbose_name_plural = _("Group Access")
        db_table = "sa_groupaccess"
        app_label = "sa"
<<<<<<< HEAD
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
=======
        ordering = ["group"]  # @todo: Sort by group__name

    group = models.ForeignKey(Group, verbose_name=_("Group"))
    selector = models.ForeignKey(ManagedObjectSelector,
            verbose_name=_("Object Selector"))

    def __unicode__(self):
        return u"(%s, %s)" % (self.group.name, self.selector.name)

    @classmethod
    def Q(cls, group):
        """
        Returns Q object
        :param cls:
        :param group:
        :return:
        """
        gq = [a.selector.Q
              for a in GroupAccess.objects.filter(group=group)]
        if gq:
            # Combine selectors
            q = gq.pop(0)
            while gq:
                q |= gq.pop(0)
            return q
        else:
            return Q(id__in=[])  # False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
