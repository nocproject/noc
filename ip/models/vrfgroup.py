# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VRFGroup model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from noc.core.translation import ugettext as _
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.fields import TagsField
from noc.lib.app.site import site
from noc.core.model.decorator import on_delete_check
from noc.core.comp import smart_text


@on_delete_check(check=[("ip.VRF", "vrf_group")])
@six.python_2_unicode_compatible
class VRFGroup(NOCModel):
    """
    Group of VRFs with common properties
    """

    class Meta(object):
        verbose_name = _("VRF Group")
        verbose_name_plural = _("VRF Groups")
        db_table = "ip_vrfgroup"
        app_label = "ip"
        ordering = ["name"]

    name = models.CharField(
        _("VRF Group"), unique=True, max_length=64, help_text=_("Unique VRF Group name")
    )
    address_constraint = models.CharField(
        _("Address Constraint"),
        max_length=1,
        choices=[
            ("V", _("Addresses are unique per VRF")),
            ("G", _("Addresses are unique per VRF Group")),
        ],
        default="V",
    )
    description = models.TextField(_("Description"), blank=True, null=True)
    tags = TagsField(_("Tags"), null=True, blank=True)

    def __str__(self):
        return smart_text(self.name)

    def get_absolute_url(self):
        return site.reverse("ip:vrfgroup:change", self.id)
