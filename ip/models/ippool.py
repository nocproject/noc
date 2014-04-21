# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IPPool model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from vrf import VRF
from afi import AFI_CHOICES
from noc.sa.models.terminationgroup import TerminationGroup

from noc.lib.fields import CIDRField
from noc.lib.validators import check_ipv4, check_ipv6


class IPPool(models.Model):
    class Meta:
        verbose_name = _("IP Pool")
        verbose_name_plural = _("IP Pools")
        db_table = "ip_ippool"
        app_label = "ip"

    termination_group = models.ForeignKey(
        TerminationGroup,
        verbose_name=_("Termination Group")
    )
    vrf = models.ForeignKey(VRF, verbose_name=_("VRF"))
    afi = models.CharField(
        _("Address Family"),
        max_length=1,
        choices=AFI_CHOICES)
    type = models.CharField(_("Type"), max_length=1, choices=[
        ("D", "Dynamic"),
        ("S", "Static")
    ])
    from_address = CIDRField(_("From Address"))
    to_address = CIDRField(_("To Address"))

    def __unicode__(self):
        return u"%s %s %s -- %s" % (
            self.termination_group.name, self.type,
            self.from_address, self.to_address)

    def clean(self):
        """
        Field validation
        """
        super(IPPool, self).clean()
        # Check prefix is of AFI type
        if self.afi == "4":
            check_ipv4(self.from_address)
            check_ipv4(self.to_address)
        elif self.afi == "6":
            check_ipv6(self.from_address)
            check_ipv6(self.to_address)
        # @todo: from_address<=to_address
        # @todo: Overlaps