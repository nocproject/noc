# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UserAccess model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
## NOC modules
from managedobjectselector import ManagedObjectSelector
from groupaccess import GroupAccess


class UserAccess(models.Model):
    class Meta:
        verbose_name = _("User Access")
        verbose_name_plural = _("User Access")
        db_table = "sa_useraccess"
        app_label = "sa"
        ordering = ["user"]  # @todo: sort by user__username

    user = models.ForeignKey(User, verbose_name=_("User"))
    selector = models.ForeignKey(ManagedObjectSelector,
            verbose_name=_("Object Selector"))

    def __unicode__(self):
        return u"(%s, %s)" % (self.user.username, self.selector.name)

    @classmethod
    def Q(cls, user):
        """
        Returns Q object for user access
        :param cls:
        :param user:
        :return:
        """
        if user.is_superuser:
            return Q() # All objects
        # Build Q for user access
        uq = [a.selector.Q
              for a in UserAccess.objects.filter(user=user)]
        if uq:
            q = uq.pop(0)
            while uq:
                q |= uq.pop(0)
        else:
            q = Q(id__in=[]) # False
        # Enlarge with group access
        for gq in [GroupAccess.Q(g) for g in user.groups.all()]:
            q |= gq
        return q
