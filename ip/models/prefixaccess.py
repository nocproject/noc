# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PrefixAccess model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from functools import reduce
from collections import defaultdict
# Third-party modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
# NOC modules
from noc.core.model.fields import CIDRField
from noc.lib.validators import check_ipv4_prefix, check_ipv6_prefix
from noc.lib.db import SQL
from .afi import AFI_CHOICES
from .vrf import VRF
from .prefix import Prefix


class PrefixAccess(models.Model):
    class Meta(object):
        verbose_name = _("Prefix Access")
        verbose_name_plural = _("Prefix Access")
        db_table = "ip_prefixaccess"
        app_label = "ip"
        unique_together = [("user", "vrf", "afi", "prefix")]
        ordering = ["user", "vrf", "afi", "prefix"]

    user = models.ForeignKey(User, verbose_name=_("User"))
    vrf = models.ForeignKey(VRF, verbose_name=_("VRF"))
    afi = models.CharField(
        _("Address Family"),
        max_length=1,
        choices=AFI_CHOICES)
    prefix = CIDRField(_("Prefix"))
    can_view = models.BooleanField(_("Can View"), default=False)
    can_change = models.BooleanField(_("Can Change"), default=False)

    def __unicode__(self):
        perms = []
        if self.can_view:
            perms += ["View"]
        if self.can_change:
            perms += ["Change"]
        return u"%s: %s(%s): %s: %s" % (
            self.user.username,
            self.vrf.name,
            self.afi, self.prefix,
            ", ".join(perms)
        )

    def clean(self):
        """
        Field validation
        :return:
        """
        super(PrefixAccess, self).clean()
        # Check prefix is of AFI type
        if self.afi == "4":
            check_ipv4_prefix(self.prefix)
        elif self.afi == "6":
            check_ipv6_prefix(self.prefix)

    @classmethod
    def user_can_view(cls, user, vrf, afi, prefix):
        """
        Check user has read access to prefix
        :param user:
        :param vrf:
        :param afi:
        :param prefix:
        :return:
        """
        if user.is_superuser:
            return True
        if isinstance(prefix, Prefix):
            prefix = prefix.prefix
        else:
            prefix = str(prefix)
        if "/" not in prefix:
            if afi == "4":
                prefix += "/32"
            else:
                prefix += "/128"
        return PrefixAccess.objects.filter(
            vrf=vrf,
            afi=afi,
            user=user,
            can_view=True
        ).extra(
            where=["prefix >>= %s"],
            params=[prefix]
        ).exists()

    @classmethod
    def user_can_change(cls, user, vrf, afi, prefix):
        """
        Check user has write access to prefix
        :param cls:
        :param user:
        :param vrf:
        :param afi:
        :param prefix:
        :return:
        """
        if user.is_superuser:
            return True
        if isinstance(prefix, Prefix):
            prefix = prefix.prefix
        else:
            prefix = str(prefix)
        if "/" not in prefix:
            if afi == "4":
                prefix += "/32"
            else:
                prefix += "/128"
        return PrefixAccess.objects.filter(
            vrf=vrf,
            afi=afi,
            user=user,
            can_change=True
        ).extra(
            where=["prefix >>= %s"],
            params=[prefix]
        ).exists()

    @classmethod
    def read_Q(cls, user, field="prefix"):
        """
        Returns django Q with read restrictions.
        Q can be applied to prefix
        :param user:
        :param vrf:
        :param afi:
        :return:
        """
        if user.is_superuser:
            return Q()  # No restrictions
        vaccess = defaultdict(set)  # (vrf, afi) -> {prefix}
        for pa in PrefixAccess.objects.filter(user=user):
            vaccess[pa.vrf.id, pa.afi].add(pa.prefix)
        if not vaccess:
            return SQL("0 = 1")  # False
        stmt = []
        for vrf, afi in vaccess:
            for p in vaccess[vrf, afi]:
                stmt += ["(vrf_id = %d AND afi = '%s' AND %s <<= '%s'" % (
                    vrf, afi, field, p
                )]
        return SQL(reduce(lambda x, y: "%s OR %s" % (x, y), stmt))
