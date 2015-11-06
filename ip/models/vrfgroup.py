# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VRFGroup model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from noc.core.model.fields import TagsField
from noc.lib.app import site


class VRFGroup(models.Model):
    """
    Group of VRFs with common properties
    """
    class Meta:
        verbose_name = _("VRF Group")
        verbose_name_plural = _("VRF Groups")
        db_table = "ip_vrfgroup"
        app_label = "ip"
        ordering = ["name"]

    name = models.CharField(
        _("VRF Group"),
        unique=True,
        max_length=64,
        help_text=_("Unique VRF Group name"))
    address_constraint = models.CharField(
        _("Address Constraint"),
        max_length=1,
        choices=[
            ("V", _("Addresses are unique per VRF")),
            ("G", _("Addresses are unique per VRF Group"))],
        default="V")
    description = models.TextField(
        _("Description"), blank=True, null=True)
    tags = TagsField(_("Tags"), null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        return site.reverse("ip:vrfgroup:change", self.id)
