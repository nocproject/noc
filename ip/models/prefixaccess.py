# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PrefixAccess model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models, connection
from django.contrib.auth.models import User
## NOC modules
from vrf import VRF
from prefix import Prefix
from afi import AFI_CHOICES
from noc.core.model.fields import CIDRField
from noc.lib.validators import check_ipv4_prefix, check_ipv6_prefix


class PrefixAccess(models.Model):
    class Meta:
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
        self.user.username, self.vrf.name, self.afi, self.prefix,
        ", ".join(perms))

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
        # @todo: PostgreSQL-independed implementation
        c = connection.cursor()
        c.execute("""SELECT COUNT(*)
                     FROM %s
                     WHERE prefix >>= %%s
                        AND vrf_id=%%s
                        AND afi=%%s
                        AND user_id=%%s
                        AND can_view=TRUE
                 """ % PrefixAccess._meta.db_table,
            [str(prefix), vrf.id, afi, user.id])
        return c.fetchall()[0][0] > 0

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
            # @todo: PostgreSQL-independed implementation
        c = connection.cursor()
        c.execute("""SELECT COUNT(*)
                     FROM %s
                     WHERE prefix >>= %%s
                        AND vrf_id=%%s
                        AND afi=%%s
                        AND user_id=%%s
                        AND can_change=TRUE
                 """ % PrefixAccess._meta.db_table,
            [str(prefix), vrf.id, afi, user.id])
        return c.fetchall()[0][0] > 0
