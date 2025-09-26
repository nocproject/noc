# ----------------------------------------------------------------------
# UserAccess model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from functools import reduce

# Third-party modules
from noc.core.translation import ugettext as _
from django.db import models
from django.db.models import Q

# NOC modules
from noc.core.model.base import NOCModel
from noc.aaa.models.user import User
from .groupaccess import GroupAccess
from .administrativedomain import AdministrativeDomain


class UserAccess(NOCModel):
    class Meta(object):
        verbose_name = _("User Access")
        verbose_name_plural = _("User Access")
        db_table = "sa_useraccess"
        app_label = "sa"
        ordering = ["user"]

    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    administrative_domain = models.ForeignKey(
        AdministrativeDomain, null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        r = ["user=%s" % self.user.username]
        if self.administrative_domain:
            r += ["domain=%s" % self.administrative_domain.name]
        return "(%s)" % ", ".join(r)

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
            if a.administrative_domain:
                domains.update(AdministrativeDomain.get_nested_ids(a.administrative_domain))
        for a in GroupAccess.objects.filter(group__in=user.groups.all()):
            if a.administrative_domain:
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
        for a in UserAccess.objects.filter(user=user, administrative_domain__isnull=False):
            domains.update(AdministrativeDomain.get_nested_ids(a.administrative_domain))
        for a in GroupAccess.objects.filter(
            group__in=user.groups.all(), administrative_domain__isnull=False
        ):
            domains.update(AdministrativeDomain.get_nested_ids(a.administrative_domain))
        return list(domains)
