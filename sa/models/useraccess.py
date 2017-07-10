# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# UserAccess model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from functools import reduce
# Third-party modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
# NOC modules
from .managedobjectselector import ManagedObjectSelector
from .groupaccess import GroupAccess
from .administrativedomain import AdministrativeDomain


class UserAccess(models.Model):
    class Meta:
        verbose_name = _("User Access")
        verbose_name_plural = _("User Access")
        db_table = "sa_useraccess"
        app_label = "sa"
        ordering = ["user"]

    user = models.ForeignKey(User, verbose_name=_("User"))
    # Legacy interface
    selector = models.ForeignKey(
        ManagedObjectSelector,
        null=True, blank=True
    )
    #
    administrative_domain = models.ForeignKey(
        AdministrativeDomain,
        null=True, blank=True
    )

    def __unicode__(self):
        r = [u"user=%s" % self.user.username]
        if self.selector:
            r += [u"selector=%s" % self.selector.name]
        if self.administrative_domain:
            r += [u"domain=%s" % self.administrative_domain.name]
        return u"(%s)" % u", ".join(r)

    @classmethod
    def Q(cls, user):
        """
        Returns Q object for user access
        :param cls:
        :param user:
        :return:
        """
        if user.is_superuser:
            return Q()  # All objects
        # Build Q for user access
        uq = []
        domains = set()
        for a in UserAccess.objects.filter(user=user):
            if a.selector:
                uq += [a.selector.Q]
            elif a.administrative_domain:
                domains.update(AdministrativeDomain.get_nested_ids(a.administrative_domain))
        for a in GroupAccess.objects.filter(group__in=user.groups.all()):
            if a.selector:
                uq += [a.selector.Q]
            elif a.administrative_domain:
                domains.update(AdministrativeDomain.get_nested_ids(a.administrative_domain))
        if domains:
            uq += [Q(administrative_domain__in=list(domains))]
        if uq:
            q = reduce(lambda x, y: x | y, uq)
        else:
            q = Q(id__in=[])  # False
        return q

    @classmethod
    def get_domains(cls, user):
        if user.is_superuser:
            return [a.id for a in AdministrativeDomain.objects.all().only("id")]
        domains = set()
        for a in UserAccess.objects.filter(
                user=user,
                administrative_domain__isnull=False
        ):
            domains.update(AdministrativeDomain.get_nested_ids(a.administrative_domain))
        for a in GroupAccess.objects.filter(
                group__in=user.groups.all(),
                administrative_domain__isnull=False
        ):
            domains.update(AdministrativeDomain.get_nested_ids(a.administrative_domain))
        return list(domains)
