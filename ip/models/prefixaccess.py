# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PrefixAccess model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from functools import reduce
from collections import defaultdict

# Third-party modules
import six
from noc.core.translation import ugettext as _
from django.db import models
from django.db.models import Q

# NOC modules
from noc.core.model.base import NOCModel
from noc.aaa.models.user import User
from noc.core.model.fields import CIDRField
from noc.core.validators import check_ipv4_prefix, check_ipv6_prefix
from noc.core.model.sql import SQL
from .afi import AFI_CHOICES
from .vrf import VRF


@six.python_2_unicode_compatible
class PrefixAccess(NOCModel):
    class Meta(object):
        verbose_name = _("Prefix Access")
        verbose_name_plural = _("Prefix Access")
        db_table = "ip_prefixaccess"
        app_label = "ip"
        unique_together = [("user", "vrf", "afi", "prefix")]
        ordering = ["user", "vrf", "afi", "prefix"]

    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    vrf = models.ForeignKey(VRF, verbose_name=_("VRF"), on_delete=models.CASCADE)
    afi = models.CharField(_("Address Family"), max_length=1, choices=AFI_CHOICES)
    prefix = CIDRField(_("Prefix"))
    can_view = models.BooleanField(_("Can View"), default=False)
    can_change = models.BooleanField(_("Can Change"), default=False)

    def __str__(self):
        perms = []
        if self.can_view:
            perms += ["View"]
        if self.can_change:
            perms += ["Change"]
        return "%s: %s(%s): %s: %s" % (
            self.user.username,
            self.vrf.name,
            self.afi,
            self.prefix,
            ", ".join(perms),
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
        return (
            PrefixAccess.objects.filter(vrf=vrf, afi=afi, user=user, can_view=True)
            .extra(where=["prefix >>= %s"], params=[prefix])
            .exists()
        )

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
        return (
            PrefixAccess.objects.filter(vrf=vrf, afi=afi, user=user, can_change=True)
            .extra(where=["prefix >>= %s"], params=[prefix])
            .exists()
        )

    @classmethod
    def read_Q(cls, user, field="prefix", table=""):
        """
        Returns django Q with read restrictions.
        Q can be applied to prefix
        :param user:
        :param field:
        :param table:
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
                stmt += [
                    "(%s = %d AND %s = '%s' AND %s <<= '%s')"
                    % (
                        "%s.vrf_id" % table if table else "vrf_id",
                        vrf,
                        "%s.afi" % table if table else "afi",
                        afi,
                        "%s.%s" % (table, field) if table else field,
                        p,
                    )
                ]
        return SQL(reduce(lambda x, y: "%s OR %s" % (x, y), stmt))


# Avoid circular references
from .prefix import Prefix
