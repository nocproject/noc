# -*- coding: utf-8 -*-
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


class GroupAccess(models.Model):
    class Meta:
        verbose_name = _("Group Access")
        verbose_name_plural = _("Group Access")
        db_table = "sa_groupaccess"
        app_label = "sa"
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
